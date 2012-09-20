from random import choice
from deck import Deck, deCanonicalize, canonicalize
from table import Table
from player import Player

class State :
    def __init__(self, \
                 table, \
                 deck = Deck(), \
                 max_raise_rounds=2) :

        self.max_raise_rounds = max_raise_rounds
 
        #bet seems superfluous, it is just the first raise
        #the numbers are for raises, pot multipliers
        self.actions = ['f','k','c','r']
        self.raises = [.5,1,1.5,2,6]
        self.final_actions = ['f','k','c']

        self.table = table
        self.num_players = self.table.num_players
    
        #virtual_player % num_players represents the player in some round
        #there are only max rounds where players are free to act 
        #(i.e keep raising)
        #+1 for the final round, players must only choose from final_actions 
        self.num_virtual = (self.num_players) * (max_raise_rounds+1)

        self.deck = deck

    def inFinalRound( self ) :
        #fogetting about button offset?
        return len(self.table.history) >= self.num_virtual - self.num_players
        pass

    def isDealerAction( self ) :
        has_acted = self.table.acted[self.table.action_to]
        oblig_is_zero = self.table.getObligation() == 0
        return has_acted and oblig_is_zero
        #return self.table.action_to % (self.num_players+1) \
                #== self.num_players

    def isChanceAction( self ) : 
        return self.isDealerAction() or \
               not self.table.action_to == self.table.toby_ix

    def playersAlive( self ) :
        alive = []
        for p in self.table.pockets :
            if p != False :
                alive.append(p)
        return alive
    
    def copy( self ) :
        snew = State( self.stacks, \
                      self.button, \
                      self.max_raise_rounds )
        snew.history = list(self.history)
        snew.pot = self.pot
        snew.stacks = self.stacks

class MCTS_Poker :
    def __init__(self, state ) :
        self.state = state
        #self.root_state = State()
        
    def copyState(self,state) :
        return state.copy()

    def isChanceAction( self, state ) :
        return state.isChanceAction()

    def getAllowableActions( self, state ) :
        if state.isChanceAction() :
            #mcts should never call expand(), and therefore getAllowable
            #when it is a dealer action
            assert False
        else :
            oblig = state.table.getObligation()
            in_final_round = state.inFinalRound()
            if oblig == 0 :
                if in_final_round :
                    return ['k'] + state.raises
                else :
                    return ['k']
            else :
                if in_final_round :
                    return ['f','c']
                else :
                    return ['f','c'] + state.raises

    def applyAction( self, state, action ) :
        if action.startswith('d') :
            state.table.advanceStreet( deCanonicalize(action) )
        else :
            pass

    def getRewards( self, state ) :
        assert self.isTerminal(state)
        one_alive = len(state.playersAlive()) == 1
        if one_alive :
            #everyone folded.  put current_bets in the pot and reward
            #do we have to track other players negative loses or just toby's
            #think just toby's considering we are treating all other players
            #as chance nodes
            #we we will need to remember toby's investment and loses in pot
            #not just how much the winner gets
            #add a investment list to table that accumulates the current_bets
            #after each round
            pass

        else :
            while state.table.street != "river" :
                cards = self.chanceAction( state )
                state.table.advanceStreet( deCanonicalize(cards) )

            #figure out winner
            #advanceStreet until the river and figure out the showdown
            pass

    def chanceAction( self, state ) :
        if state.isDealerAction() :
            if state.table.street == "preflop" :
                cards = state.deck.draw(3)
            elif state.table.street == "flop" or \
                 state.table.street == "turn" :
                cards = state.deck.draw(1)
            return "d%s" % canonicalize(cards)

        else :
            player = state.table.players[state.table.action_to]
            return player.getAction( state )


    #TODO
    #This is where we implement the naive player
    #The million dollar question
    def opponentAction(self, opp_ix, state ) :
        pass

    def isTerminal( self, state ) :
        #TODO: all but one player all-in
        one_alive = len(state.playersAlive()) == 1

        only_one_stack_left = sum([state.table.stacks[pix] > 0 \
                                   for pix \
                                   in range(state.table.num_players)
                                   if state.table.pockets[pix] ]) == 1 

        print "only_one_stack_left", only_one_stack_left
        print "is dealer action:" , state.isDealerAction()
        showdown = state.isDealerAction() and \
                   (state.table.street == 'river' or \
                    only_one_stack_left)
        return one_alive or showdown

def main() :
    p1 = Player("toby")
    d = Deck()
    toby_ix = 0
    toby_pockets = d.draw(2)
    p2 = Player("frylock")
    players = [p1,p2]
    stacks = [1.5,100]
    t = Table(players, stacks, toby_ix, toby_pockets )
    t.pot = 3
    s = State( t, d ) 

    mcts = MCTS_Poker( s )

    print mcts.state.table
    mcts.state.table.registerAction( 'k' )
    mcts.state.table.registerAction( 'r', .5 )
    mcts.state.table.registerAction( 'r', .5 )
    #since toby is out of money here, frylock should auto-check
    #or rather getAllowableActions should only return k here
    mcts.state.table.registerAction( 'k' )
    
    print mcts.state.table

    print "final round?: ",mcts.state.inFinalRound()
    #print "Allowable: ", mcts.getAllowableActions( s )
    #mcts.state.table.registerAction( 'f' )

    print "terminal?: ", mcts.isTerminal(s)
    print "rewards:", mcts.getRewards(s)
    print mcts.state.table

if __name__ == '__main__' :
    main()
