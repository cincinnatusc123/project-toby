BET_RATIOS = [0,.2,.3,.4,.5,.75,1]
BUCKET_PERCENTILES = {'flop' : [.4,.1,.1] + [.05]*4 + [.02]*10, \
                      'turn' : [.4,.1,.1] + [.05]*4 + [.02]*10, \
                      'river': [.45,.15,.14,.05,.05,.05,.05,.02,.02,.02] }

BUCKET_PERCENTILES_SMALL = {'flop' : [.4,.2,.15,.10,.08,.07], \
                            'turn' : [.4,.3,.2,.1], \
                            'river' : [.5,.5] }

#see exponential.py
BUCKET_PERCENTILES_EXPO = {'preflop' : [0.40003900044927887, 0.24004940056908658, 0.14407297417398401, 0.08651600755861058, 0.05202997629219996, 0.03141860537037599, 0.019185529213985624, 0.012068594181324752, 0.008169950930350486, 0.006449961260803015], \
                           'flop' : [0.25000586640034034, 0.18750635526703532, 0.1406323737393166, 0.10547775668987426, 0.07911295269792144, 0.059340894764128745, 0.04451391139401344, 0.033396420640065934, 0.025061964939457244, 0.01881600631713666, 0.01413804822124413, 0.010638260810455278, 0.008024995133871034, 0.0060804790517760415, 0.004642669557329053, 0.003591749192659485, 0.0028401412607115414, 0.0023252117671562263, 0.0020040499208639297, 0.0018498922346436276], \
                           'turn' : [0.3000164218894933, 0.21001853327528525, 0.14702302751075672, 0.10293048242618265, 0.07207185651068919, 0.05047961214657008, 0.035377603629867124, 0.02482414415128994, 0.017462360349307173, 0.012345737163663904, 0.00881642304192028, 0.006420649025566406, 0.004850387026785357, 0.003903746217162425, 0.0034590156354603763], 
                           'river' : [0.3501610588099545, 0.22769141220106134, 0.14813283943006045, 0.09649160947472483, 0.0630353366896258, 0.041458800434494715, 0.027695653492018392, 0.019152072015345536, 0.014217919495410875, 0.011963297957303649] }

BUCKET_TABLE_PREFIX = "BUCKET_EXPO"


EVALUATOR = "pokereval"
GAME = 'holdem'
NA = 'xx'
if GAME == 'holdem' or GAME == 'omaha' :
    #STREET_NAMES = ["undealt","preflop","flop","turn","river","over"]
    STREET_NAMES = [-1,0,1,2,3,4]

if GAME == 'holdem' :
    POCKET_SIZE = 2

if EVALUATOR == 'pokereval' :
    #numerical rep of a folded card
    FOLDED = 254

    #numerical rep of an unknown
    WILDCARD = 255

    #Computed EV can range from from 0-1000
    EV_RANGE = 1000


def veryClose( a,b,p=.00001 ) :
    return abs(a-b) < p
