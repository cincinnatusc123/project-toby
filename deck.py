from itertools import combinations
from random import sample
from pokereval import PokerEval
import globles
import re

#this is the suit ordering that PokerEval uses
suits = ('h','d','c','s')
pe = PokerEval()

#annoyingly, pokereval API doesn't give a way to do this
def getCardinality( card ) :
    if type(card) == int :
        return (card % 13)+2
    elif type(card) == str :
        return intifyCardinality(card[0])
    else :
        assert "go" == "fuck yourself"

#annoyingly, pokereval API doesn't give a way to do this
def getSuit( card ) :
    if type(card) == int :
        return suits[card / 13]
    elif type(card) == str :
        return card[1]
    else :
        assert "go" == "fuck yourself"

#take integers and output card string
def makeHuman( cards ) :
    #if already in right format, leave alone
    if len(cards) == 0 : return []
    if type(cards[0]) == str : return cards
    r = []
    for c in cards :
        if c == globles.FOLDED : 
            r.append('x')
        else :
            r.append( pe.card2string(c) )
    return r

#take strings and output card number
def makeMachine( cards ) :
    #if already in right format, leave alone
    if len(cards) == 0 or type(cards[0]) == int : return cards
    r = []
    for c in cards :
        if c == 'x' :
            r.append(globles.FOLDED)
        else :
            r.append( pe.string2card(c) )
    return r

CARDINALITIES = [str(v) for v in range(2,10)] + ['T','J','Q','K','A']
def stringifyCardinality( c ) :
    d = {}
    for i in range(2,15) :
        d[i] = CARDINALITIES[i-2]
    #d = {2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9', \
         #10:'T',11:'J',12:'Q',13:'K',14:'A'}
    return d[c]

def intifyCardinality( c ) :
    d = {}
    for i,card in enumerate(CARDINALITIES) :
        d[card] = i+2
    return d[c]

#return a comma separated list of human readable cards, sorted by numeric value
def canonicalize( cards ) :
    if type(cards) == str :
        cards = listify(cards)
    cards = makeMachine(cards)
    cards.sort()
    return ''.join( makeHuman(cards) )

#used anywhere?
suit_split = re.compile(r'([hsdc])')
def deCanonicalize( card_string ) :
    if card_string.startswith('d') : card_string = card_string[1:]
    splt = suit_split.split( card_string )[:-1]
    return [ "%s%s" % (splt[i],splt[i+1]) \
             for i \
             in range(0,len(splt),2) ]

#turn card string into list
def listify( card_string ) :
    cards = [card_string[i:i+2] \
             for i in range(0,len(card_string),2)]
    return cards

def isStraight( sorted_cardinalities ) :
    if sorted_cardinalities[-1] == 14 :
        if isStraight( [1] + sorted_cardinalities[0:-1] ) :
            return True
      
    value = -1
    l = len(sorted_cardinalities) - 1
    for i,c in enumerate(sorted_cardinalities) :
        i = l - i
        if value == -1 :
            value = i+c
        else :
            if not i+c == value : return False
    return True

#return the distinct type of hole card (1326 -> 169)
#hole_cards are [int,int]
def collapsePocket( hole_cards ) :
    c1 = getCardinality(hole_cards[0])
    c2 = getCardinality(hole_cards[1])
    s1 = getSuit(hole_cards[0])
    s2 = getSuit(hole_cards[1])
    if s1 == s2 :
        suit = 's'
    else:
        suit = 'o'

    if c1 < c2 :
        return ('%s%s%s' % (stringifyCardinality(c1), \
                            stringifyCardinality(c2), \
                            suit) )
    elif c1 == c2 :
        return ('%s%s' % (stringifyCardinality(c1), \
                          stringifyCardinality(c2)))
    else :
        return ('%s%s%s' % (stringifyCardinality(c1), \
                            stringifyCardinality(c2),
                            suit) )

def collapseBoard( board ) :
    if type(board) == str :
        board = [board[i:i+2] for i in range(0,len(board),2)]
    board = truncate(board)
    board = sorted(board, key=lambda c : getCardinality(c))

    cardinalities = [getCardinality(c) for c in board]
    card_counts = {}
    for c in cardinalities :
        if c in card_counts :
            card_counts[c] += 1
        else :
            card_counts[c] = 1
    #cardinalities.sort()
    num_cardinalities = len(card_counts.keys()) #set(cardinalities))
    
    suits = [getSuit(c) for c in board]
    suit_counts = {}
    max_suit, max_suit_count = 'uninit',0
    for s in suits :
        if s in suit_counts :
            suit_counts[s] += 1
        else:
            suit_counts[s] = 1
        if suit_counts[s] > max_suit_count :
            max_suit_count = suit_counts[s]
            max_suit = s
    num_suits = len(set(suits))

    if len(board) == 3 :
        if   num_cardinalities == 1 : rcard = 't'
        elif num_cardinalities == 2 : rcard = 'p'
        else :
            if isStraight(cardinalities) : rcard = 's'
            else :                         rcard = 'h'

        if   num_suits == 1 : rsuit = '3f'
        elif num_suits == 2 : 
            if rcard == 'p' :
                rsuit = '2f'
            else :
                if   suits[0] == suits[1] : rsuit = '2fxxo'
                elif suits[0] == suits[2] : rsuit = '2fxox'
                elif suits[1] == suits[2] : rsuit = '2foxx'
                else : 
                    print "assert 1"
                    assert False
        else                : rsuit = 'r'

        #s3f  3-Straight-Flush = 12
        #t    Trips = 13
        #s2f 3-Straight 2-flush = 12 * 3 = 36
        #sr   3-Straight rainbow = 12
        #3f    3-Flush = c(13,3)-12 = 274
        #pr   Paired rainbow = 13 *12 = 156
        #p2f  Paired 2-flush = 13 * 12 = 156
        #h2f  High-Card-Flops 2-flush: [c(13,3)-12] * 3 = 822
        #hr   High-Card-Flops Rainbow: [c(13,3)-12] = 274
    elif len(board) == 4 : 
        if   num_cardinalities == 1 : rcard = 'q'
        elif num_cardinalities == 2 : 
            counts = list(card_counts.values())
            if counts[0] == counts[1] == 2 :
                rcard = '2p'
            else :
                rcard = 't'
        elif num_cardinalities == 3 :
            rcard = 'p'
        else :
            if isStraight(cardinalities) : rcard = 's'
            else :                         rcard = 'h'

        if   num_suits == 1 : rsuit = '4f'
        elif num_suits == 2 : 
            #impossible with: quads, trips
            if rcard == 'p' :
                rsuit = '3f'
            elif rcard == '2p' :
                rsuit = '22f'
            elif rcard == 'h' or rcard == 's' : 
                if   suits[0] == suits[1] == suits[2] : rsuit = '3fxxxo'
                elif suits[0] == suits[1] == suits[3] : rsuit = '3fxxox'
                elif suits[0] == suits[2] == suits[3] : rsuit = '3fxoxx'
                elif suits[1] == suits[2] == suits[3] : rsuit = '3foxxx'
                elif suits[0] == suits[1] and suits[2] == suits[3] :
                    rsuit = '22fxxoo'
                elif suits[0] == suits[2] and suits[1] == suits[3] :
                    rsuit = '22fxoxo'
                elif suits[0] == suits[3] and suits[1] == suits[2] :
                    rsuit = '22fxoox'
                else :
                    print suits
                    assert False
            else :
                print rcard
                assert False
        elif num_suits == 3 :
            if rcard == 'p' or rcard == 'h' or rcard == 's' :
                if   suits[0] == suits[1] : temp = 'xxoo'
                elif suits[0] == suits[2] : temp = 'xoxo'
                elif suits[0] == suits[3] : temp = 'xoox'
                elif suits[1] == suits[2] : temp = 'oxxo'
                elif suits[1] == suits[3] : temp = 'oxox'
                elif suits[2] == suits[3] : temp = 'ooxx'
                else : 
                    assert False

                if rcard == 'p' :
                    for c in card_counts :
                        if card_counts[c] == 2 :
                            ix = cardinalities.index(c)
                    sub = temp[ix:ix+2]
                    if sub == 'ox' or sub == 'xo' :
                        temp = temp[:ix] + 'x' + temp[ix+2:]
                    elif sub == 'oo' :
                        temp = temp[:ix] + 'o' + temp[ix+2:]
                    else :
                        assert False

                rsuit = '2f' + temp

            elif rcard == '2p' :
                rsuit = '2f'
            elif rcard == 't' :
                rsuit = '2f'
            elif rcard == 'h' :
                pass
            else : 
                print rcard
                assert False
        else                : rsuit = 'r'

    elif len(board) == 5 : 
        if   num_cardinalities == 1 : 
            assert False
        elif num_cardinalities == 2 : 
            if max( card_counts.values() ) == 3 :
                rcard = 'b'#oat
            else :
                rcard = 'q'
        elif num_cardinalities == 3 : 
            if max( card_counts.values() ) == 2 :
                rcard = '2p'
            else :
                rcard = 't'
        elif num_cardinalities == 4 : 
            rcard = 'p'
        elif num_cardinalities == 5 :
            if isStraight(cardinalities) : rcard = 's'
            else                         : rcard = 'h'

        if num_suits == 1 :
            rsuit = '5f'
        elif num_suits == 2 :
            #max_suit_count = max( suit_counts.values() )
            if max_suit_count == 4 :
                if rcard == 'p' :
                    rsuit = '4f'
                elif rcard == 'h' or rcard == 's' :
                    rsuit = ['4f']
                    for i in range(5) :
                        if suits[i] != max_suit :
                            rsuit.append('o')
                        else :
                            rsuit.append('x')
                    rsuit = ''.join(rsuit)
                    #rsuit = '4f'+ 'x'*i + 'o' + 'x'*(5-i-1)
                else:
                    assert False
            elif max_suit_count == 3 :
                if rcard == 'p' :
                    for c in card_counts :
                        if card_counts[c] == 2 :
                            pair_ix = cardinalities.index(c)
                            break
                    rsuit = ['3f']
                    for i in range(5) :
                        if i == pair_ix :
                            rsuit.append('x')
                        elif i == pair_ix+1 : 
                            rsuit.append('o')
                        elif suits[i] == max_suit :
                            rsuit.append('x')
                        else :
                            rsuit.append('o')
                elif rcard == '2p' :
                    pair_ixs = set([])
                    for c in card_counts :
                        if card_counts[c] == 2 :
                            pair_ixs.add( cardinalities.index(c) )
                    rsuit = ['3f']
                    for i in range(5) :
                        if i in pair_ixs :
                            rsuit.append('x')
                        elif i-1 in pair_ixs :
                            rsuit.append('o')
                        else :
                            rsuit.append('x')
                elif rcard == 'h' or rcard == 's' :
                    rsuit = ['3f']
                    for i in range(5) :
                        if suits[i] == max_suit :
                            rsuit.append('x')
                        else :
                            rsuit.append('o')
                else :
                    assert False
                
                rsuit = ''.join(rsuit)

            else :
                pass

        elif num_suits == 3 :
            if max_suit_count < 3 :
                rsuit = "r" 
            else :
                rsuit = ['3f']
                if rcard == 'p' :
                    for c in card_counts :
                        if card_counts[c] == 2 :
                            pair_ix = cardinalities.index(c)
                            break
                    pair_has_max_suit = suits[pair_ix] == max_suit or \
                                        suits[pair_ix+1] == max_suit
                    if pair_has_max_suit :
                        for i in range(5) :
                            if i == pair_ix :
                                rsuit.append('x')
                            elif i == pair_ix+1 :
                                rsuit.append('o')
                            elif suits[i] == max_suit :
                                rsuit.append('x')
                            else :
                                rsuit.append('o')
                    else :
                        for i in range(5) :
                            if suits[i] == max_suit :
                                rsuit.append('x')
                            else :
                                rsuit.append('o')

                elif rcard == '2p' :
                    #same as num_suits == 2
                    pair_ixs = set([])
                    for c in card_counts :
                        if card_counts[c] == 2 :
                            pair_ixs.add( cardinalities.index(c) )
                    rsuit = ['3f']
                    for i in range(5) :
                        if i in pair_ixs :
                            rsuit.append('x')
                        elif i-1 in pair_ixs :
                            rsuit.append('o')
                        else :
                            rsuit.append('x')

                elif rcard == 't' :
                    for c in card_counts :
                        if card_counts[c] == 3 :
                            trip_ix = cardinalities.index(c)
                            break
                    rsuit = ['3f']
                    for i in range(5) :
                        if i == trip_ix or \
                           i == trip_ix + 1 or \
                           i == trip_ix + 2:
                            rsuit.append('x')
                        else :
                            rsuit.append('o')
                elif rcard == 's' or rcard == 'h' :
                    for i in range(5) :
                        if suits[i] == max_suit :
                            rsuit.append('x')
                        else :
                            rsuit.append('o')
                else :
                    assert False
                rsuit = ''.join(rsuit)

        elif num_suits == 4 :
            rsuit = "r"
        else :
            assert False
    else :
        assert False

    crdnlts = ''.join([stringifyCardinality(c) for c in cardinalities])
    return "%s_%s_%s" % (crdnlts, rcard, rsuit)

def isAssignmentLegal( pocket, board ) :
    pocket = makeMachine(pocket)
    board = makeMachine(board)
    for p in pocket :
        if p in board : return False
    return True


#returns the pocketp that satisfies:
#'pocketp' : 'boardp' :: 'pocket' : 'board' 
def symmetricComplement( board, pocket, boardp ) :
    legal = isAssignmentLegal( pocket, board ) 
    if not legal : return False
    cboard = collapseBoard(board)

    #if the board is a rainbow, it doesn't matter what the mapping is
    #it only matters that pocketp has the right cardinalities, and that
    #the cards do not conflict with boardp
    is_rainbow = cboard[-1] == 'r'
    if is_rainbow :
        #pick two cards of correct cardinality that don't conflict with boardp
        pocketp = [-1,-1]
        for pix in range(len(pocket)) :
            p = pocket[pix]
            card,suit = stringifyCardinality(getCardinality(p)),getSuit(p)
            suits = [suit,'h','d','c','s']
            found = False
            for s in suits :
                if card+s not in boardp :
                    pocketp[pix] = card+s
                    found = True
                    break
            assert found
        return canonicalize(pocketp)

    #idea is to match determine the functionally important suits in board
    #and match them to those in boardp (i.e suit count >= 2 )

    #info about the suits in board
    board_suits = [getSuit(c) for c in board]
    board_suit_counts = {}
    board_max_suit, board_max_suit_count = 'uninit',0
    for s in board_suits :
        if s in board_suit_counts :
            board_suit_counts[s] += 1
        else:
            board_suit_counts[s] = 1
        if board_suit_counts[s] > board_max_suit_count :
            board_max_suit_count = board_suit_counts[s]
            board_max_suit = s

    #info about the suits in boardp
    boardp_suits = [getSuit(c) for c in boardp]
    boardp_suit_counts = {}
    boardp_max_suit, boardp_max_suit_count = 'uninit',0
    for s in boardp_suits :
        if s in boardp_suit_counts :
            boardp_suit_counts[s] += 1
        else:
            boardp_suit_counts[s] = 1
        if boardp_suit_counts[s] > boardp_max_suit_count :
            boardp_max_suit_count = boardp_suit_counts[s]
            boardp_max_suit = s

    assert boardp_max_suit_count == board_max_suit_count

    #sort the suits for each board in descending order according to their counts
    board_sorted_suits = sorted( board_suit_counts, \
                                 key = lambda s:board_suit_counts[s], \
                                 reverse=True )
    boardp_sorted_suits = sorted( boardp_suit_counts, \
                                  key = lambda s:boardp_suit_counts[s], \
                                  reverse=True )

    #will hold the final suit mapping
    suit_map = {}

    #these hold the suits not yet used in suit_map
    suits = set(['h','d','c','s'])
    suitsp = set(['h','d','c','s'])

    #map the most frequent suits in each board together
    for bsuit, bpsuit in zip(board_sorted_suits, boardp_sorted_suits) :
        if board_suit_counts[bsuit] > 1 and boardp_suit_counts[bpsuit] > 1 :
            suit_map[bsuit] = bpsuit
            suits.remove(bsuit)
            suitsp.remove(bpsuit)
        else :
            #can be of count 2 in one board and 1 in the other
            #e.g river with 3f and 2f, and 3f and 1f 1f.
            pass

    #print "intermediate suit_map: " , suit_map

    #now map the remaining suits
    #-
    #first, recognize that some mappings are illegal
    #consider board: [2c 3c 4c 8h 9d] and pokcet [7d Kh]
    #        boardp: [2d 3d 4d 7s 9s]
    #obviously c -> d.  But if we pick d -> s, 7d->7s, which is impossible
    #according to boardp
    #illegal_map = {board_suit : {boardp_suit : 1, ...} , ... }
    illegal_map = {}
    for p in pocket :
        #print pocket
        pc = getCardinality(p)
        ps = getSuit(p)
        for b in boardp :
            bc = getCardinality(b)
            bs = getSuit(b)
            if pc == bc and ps not in suit_map :
                #print "!", pc,ps,bc,bs
                if ps in illegal_map :
                    illegal_map[ps][bs] = True
                else :
                    illegal_map[ps] = {bs:True}
    #print "illegal_map:", illegal_map

    #now we are ready to finish the mapping
    #first map the suits that have illegal mappings
    
    #since we cannot modify a collection as we iterate through it,
    #we maintain 'used' to prohibit future mappings to use a suit that
    #has just been assigned
    used = {}
    for s in illegal_map :
        #print "illegal suit: ", s, illegal_map[s]
        for sp in suitsp :
            if sp not in used and sp not in illegal_map[s] :
                suit_map[s] = sp
                #if s in suits :
                suits.remove(s)
                #print suit_map, suits, suitsp
                used[sp] = True 
                break

    #arbitrarily map the remaining minority suits to one another
    for s in suits :
        #print "s",s
        for sp in suitsp :
            #print "sp",sp
            if sp not in used :
                #print "mapping", s, " to " , sp
                suit_map[s] = sp
                used[sp] = True
                break
            else :
                pass
                #print "not allowed"

    print "sm: ", suit_map

    #apply the mapping
    pocket = canonicalize(pocket) #sorted( pocket, key=lambda x:x[0] )
    #print suit_map
    pocketp = []
    for c in pocket :
        if c in suit_map :
            pocketp.append( suit_map[c] )
        else :
            pocketp.append( c )
    return canonicalize( ''.join(pocketp) )

def getStreet( board ) :
    num_unknown = sum([c == '__' for c in board])
    if   num_unknown == 5 : return 'preflop'
    elif num_unknown == 2 : return 'flop'
    elif num_unknown == 1 : return 'turn'
    elif num_unknown == 0 : return 'river'

def truncate( board ) :
    try :
        return board[0:board.index('__')]
    except ValueError :
        return board
 
#would be cool to stream possible hole card combinations given
#our best guess at each players holding distribution.  

class Deck:
    def __init__(self) :
        #print "deck init: " , set_of_cards
        self.cards = set(range(52))
    
    def shuffle(self) :
        self.cards = set(range(52))

    def copy(self) :
        return Deck( set(self.cards) )

    #if all the cards are present to be be removed, do so and return True
    #if not, do not remove anything and return False
    def remove( self, cards ) :
        cards = makeMachine(cards)
        try :
            removed = []
            for c in cards : 
                if c < 52 :
                    self.cards.remove(c)
                    removed.append(c) 
            return True
        except KeyError as ve :
            self.replace( removed )
            return False

    #since d.cards is a set don't need to worry about duplicates
    def replace( self, cards ) :
        for c in cards : self.cards.add(c)

    #draw n at random from the cards remaining in the deck
    def draw( self, n ) :
        selections = sample(self.cards, n)
        self.remove( selections )
        return selections
        #return tuple( humancards[s] for s in selections )    

def main() :
    #d = Deck()
    #d.remove([1,2,3])
    #d.remove([4,1])
#
    #print collapsePocket([25,51])
    #print makeMachine(['2h','As'])
    #print numPocketsMakeStraight([10,13,14])
    #print collapseBoard(['3d','7c','7s','7h'])
    print deCanonical( '3d8cTs' )

if __name__ == '__main__' :
    board = ['3h','Qh','3d','Kh']
    boardp= ['3s','Qh','Kh','3h']
    pocket = ['5d','7s']

    print collapseBoard(['2h','3h','4h','9h','Kd'])
    print collapseBoard(['2h','3h','4s','9h','Kh'])

    #print symmetricComplement( board, pocket,\
                         #boardp )

    #main()


    #fout = open( "fullboard_collapse_test.txt", 'w' )
    #d = Deck()
    #count = 0
    #seen = set()
    #temp = []
    #for board in combinations( d.cards, 5 ) :
        #if count % 10000 == 0 : print count
        #collapsed = collapseBoard( board )
        #if collapsed in seen :
            #pass
        #else :
            #temp.append( collapsed )
            #seen.add( collapsed )
#
        #count += 1
#
    #fout.write( '\n'.join(temp) )
    #fout.close()
    
    
    
    #print collapseBoard( ['7s','6h','8h','6s','8s'] )



