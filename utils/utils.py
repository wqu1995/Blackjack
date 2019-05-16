
deck = [1,2,3,4,5,6,7,8,9,10]

HIT = 0
STAND = 1
FORFEIT = 2
ACTIONS = [HIT, STAND, FORFEIT]

P1 = 1
P2 = -P1
CHANCE = 0

def draw_card(np_random):
    return int(np_random.choice(deck))

def usable_ace(hand):
    return 1 in hand

def sum_hand(hand):
    if usable_ace(hand):
        return sum(hand)+10
    return sum(hand)

def is_bust(hand):
    return sum_hand(hand) > 21


def cmp(a, b):
    #a = p1
    #b = p2
    if sum_hand(a) > sum_hand(b):
        return 1
    elif sum_hand(a) < sum_hand(b):
        return -1
    else:
        return 0

def init_sigma(root):
    print(root)

def init_empty_node_maps(root):
    print(root)


