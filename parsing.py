import re
import os
import os.path
import table
import json
from globles import veryClose

MIN_BET_THRESH = 1
ALL_IN_THRESH = .8

re_game_id = re.compile(r'\*\*\*\*\* Hand History for Game (\d+) \*\*\*\*\*')
re_table_name = re.compile(r'Table (.*) \(Real Money\)')
re_button = re.compile(r'Seat (\d) is the button')
re_num_players = re.compile(r'Total number of players : (\d)/(\d)')
re_pip = re.compile(r'(.*) (posts small blind|posts big blind|is all-In|raises|bets|calls) \[\$(\d+)(\.(\d\d))? USD\].*')
re_checkfold = re.compile(r'(.*) (checks|folds)')
re_seat = re.compile(r'Seat (\d): (.*) \( \$(\d+)(\.(\d\d))? USD \)')
re_dealing = re.compile(r'\*\* Dealing (.*) \*\* (.*)')
re_end = re.compile(r'(.*) wins \$(\d+)(\.(\d\d))? USD from the main pot.')

def concatentateHistories( parent_dir ) :
    fout = open( "%s/histories.txt" % parent_dir, 'wb' )
    fout.write("\n")
    for history_file in os.listdir( parent_dir ) :
        if history_file.startswith("pty") :
            handle = open("%s/%s" % (parent_dir,history_file), 'U' )
            firstline = handle.readline()
            fout.write( firstline.decode('utf-8').encode('ascii','ignore') )
            fout.write( handle.read() )
            #fout.write("\n\n")
    fout.close()

def splitHistoryFileByTable( history_filename ) :
    fin = open("%s.txt" % history_filename)
    if os.path.exists( history_filename ) :
        print "already parsed %s" % filename
        return

    os.mkdir( history_filename ) 
    #tablename : [game_lines1, game_lines2,...]
    table_gamedata = {}
    current_gamedata = []
    current_table = ""

    for line in fin.readlines() :
        line = line.strip()
        new_game_match = re_game_id.match(line)
        if new_game_match :
            if current_table not in table_gamedata :
                table_gamedata[current_table] = []
            table_gamedata[current_table].append("\n".join(current_gamedata))

            current_gamedata = [line]
            current_table = ""
        else :
            current_gamedata.append(line)
            table_match = re_table_name.match(line)
            if table_match :
                current_table = table_match.groups(1)
    
    #add in the last game
    if current_table not in table_gamedata :
        table_gamedata[current_table] = []
    table_gamedata[current_table].append("\n".join(current_gamedata))

    for table_id, table in enumerate(table_gamedata) :
        fout = open( "%s/table-%s.txt" % (history_filename, table_id), 'w' )
        fout.write( "\n\n".join( table_gamedata[table] ) )
        fout.close()

#convert regexp groups to a float amount
def reGroupsToAmount( dollar_group, cent_group ) :
    dollars = int(dollar_group)
    if cent_group :
        cents = float(cent_group) / 100
    else : cents = 0
    return dollars+cents

def extractBidFeatures( filename ) :
    mapping = False

    fin = open( filename )
 
    t = table.Table(small_blind=.5)
    isfirst = True
    line_count = 0
    line = fin.readline()
    not_zero_count = 0
    zero_or_one_count = 0
    while line :
        line = line.strip()
        new_game_match = re_game_id.match(line)
        if new_game_match :
            if not isfirst :
                pass
                #print t
                #print t.features
                #assert False
            
            isfirst = False
            print "\n\n"
            print new_game_match.group(1)
            #TODO finish processing last game
            
            #setup hand
            fin.readline().strip()
            fin.readline().strip()
            button_line = fin.readline().strip()
            num_players_line = fin.readline().strip()
            num_players_match = re_num_players.match( num_players_line )
            num_players, num_seats = int(num_players_match.group(1)), \
                                     int(num_players_match.group(2))

            button_match = re_button.match( button_line )
            seat_button = int(button_match.group(1))
            #button = button - num_seats + 1
            #print "button: ", button

            players = []
            pockets = [["__","__"]]*num_players
            stacks = [] 
            button = 0

            zero_stacked_player = False
            for player in range(1,num_players+1) :
                seat_name_line = fin.readline().strip()
                seat_match = re_seat.match( seat_name_line )
                player_seat = int(seat_match.group(1))
                player_name = seat_match.group(2)
                if player_seat < seat_button :
                    button += 1
                stack = reGroupsToAmount( seat_match.group(3), \
                                         seat_match.group(5) )

                #if player has stack of 0, ignore and fastforward to next hand 
                if stack == 0 :
                    end_match = False
                    while not end_match :
                        line = fin.readline().strip()
                        end_match = re_end.match(line)
                    zero_stacked_player = True
                    break

                players.append( player_name )
                stacks.append( stack )
            if zero_stacked_player : continue
            
            t.newHand(players, pockets, stacks, button)

            #small blind
            match_pip = re_pip.match( fin.readline().strip() )
            bet = reGroupsToAmount( match_pip.group(3), match_pip.group(5) )
            assert( bet == t.small_blind )
            t.registerAction( 'c' )

            #big blind
            match_pip = re_pip.match( fin.readline().strip() )
            bet = reGroupsToAmount( match_pip.group(3), match_pip.group(5) )
            t.registerAction( 'c' )
            #t.registerAction( 'r', 1 )


            assert( fin.readline().strip() == "** Dealing down cards **" )

        else :
            match_pip = re_pip.match(line)
            if match_pip :
                player = match_pip.group(1)
                assert( t.players.index(player) == t.action_to )
                action = match_pip.group(2)
                bet = reGroupsToAmount( match_pip.group(3), match_pip.group(5) )
                #print player, action, bet
                if action == "raises" or action == "bets" :
                    t.registerAction( action[0], bet )
                elif action == "is all-In" :
                    t.registerAction( 'a', bet )
                else : #calls
                    t.registerAction( action )
                #t.extractFeatures()
            else :
                checkfold_match = re_checkfold.match(line)
                if checkfold_match :
                    action = checkfold_match.group(2)
                    if action == 'checks' :
                        t.registerAction( 'c' )
                    else :
                        t.registerAction( 'f' )
                else :
                    dealing_match = re_dealing.match( line )
                    if dealing_match :
                        street = dealing_match.group(1)
                        cards = dealing_match.group(2)
                        cards = cards[1:-1].replace(" ","").split(",")
                        pip_ratios = t.advanceStreet(cards)
                        yield pip_ratios
                    else :
                        end_match = re_end.match(line)
                        if end_match :
                            #winning_pix = t.players.index( end_match.group(1) )
                            win_amt = reGroupsToAmount( end_match.group(2), \
                                                        end_match.group(4) )
                            pip_ratios = t.advanceStreet(False)

                            if len(pip_ratios) >= 2 :
                                if 0< pip_ratios[1][2] < 1 :
                                    not_zero_count += win_amt 
                                    print win_amt, pip_ratios[1][2]
                                else :
                                    zero_or_one_count += win_amt
                            #for repeat in range( int(win_amt) ) :
                            yield pip_ratios
                        else :
                            pass

        line = fin.readline()
        line_count += 1
        

    print "adsfasdfwegfwad"
    print not_zero_count
    print zero_or_one_count
    fin.close()

#calls extractBidFeatures
def splitBidFeaturesByStreet( filename ) :
    features = [[],[],[],[]]
    for bid_feature in extractBidFeatures( "%s.txt" % filename ) :
        #print bid_feature
        street = bid_feature[0]
        for player in range( 1,len(bid_feature) ) :
            features[street].append( bid_feature[player] )

    fpre = open( "%s_preflop_bid_features.txt" % filename, 'w' )
    fflop = open( "%s_flop_bid_features.txt" % filename, 'w' )
    fturn = open( "%s_turn_bid_features.txt" % filename, 'w' )
    friver = open( "%s_river_bid_features.txt" % filename, 'w' )
    fpre.write( json.dumps( features[0] ) )
    fflop.write( json.dumps( features[1] ) )
    fturn.write( json.dumps( features[2] ) )
    friver.write( json.dumps( features[3] ) )
    fpre.close()
    fflop.close()
    fturn.close()
    friver.close()

if __name__ == '__main__' :
    #filename = "histories/knufelbrujk_hotmail_com_PTY_NLH100_3-6plrs_x10k_1badb/pty NLH handhq_%d"
    #filename = "histories/knufelbrujk_hotmail_com_PTY_NLH100_2-2plrs_x10k_f8534/pty NLH handhq_0"
    filename = "histories/knufelbrujk_hotmail_com_PTY_NLH100_2-2plrs_x10k_f8534/histories"


    #splitHistoryFileByTable(filename)
    #concatentateHistories( "histories/knufelbrujk_hotmail_com_PTY_NLH100_2-2plrs_x10k_f8534" )

    splitBidFeaturesByStreet( filename )

    #street = "flop"
    #col = 2 
    #bid_features = json.loads( open("histories/knufelbrujk_hotmail_com_PTY_NLH100_2-2plrs_x10k_f8534/histories_%s_bid_features.txt" % street).read() )
    #open("histories/knufelbrujk_hotmail_com_PTY_NLH100_2-2plrs_x10k_f8534/agg_to_pip_%s.txt" % street ,'w').write( json.dumps( [bf[col] for bf in bid_features if bf[col] > 0]) )

