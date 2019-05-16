from utils.utils import *
from model.game import *
import pytest

def __recursive_tree_assert(root, logical_expression):
    assert logical_expression(root)
    for k in root.children:
        __recursive_tree_assert(root.children[k], logical_expression)

def test_game_tree_actions_number_equal_to_children():
    root = BlackJackRoot()
    temp = root.children[0]
    temp.play(HIT)
    assert len(temp.children) == 3
    #__recursive_tree_assert(root, lambda node: len(node.children) == 0)

def test_root_chance():
    root = BlackJackRoot()
    assert root.player == CHANCE

def test_player1_move_first():
    root = BlackJackRoot()
    for k in root.children:
        assert k.player == P1

def test_card():
    root = BlackJackRoot()
    assert root.inf_set() == "."
    temp = root.children[3]
    assert temp.player_pub == [1]
    assert temp.player_priv == 1
    assert temp.op_pub == [1]
    assert temp.op_priv == 4
    assert temp.player == P1

    #p1 infoset
    assert temp.info_set() == ([1,1],[1],[])
    assert temp.player == P1
    #p2 infoset
    temp.construct_child()
    temp = temp.play(STAND)
    assert temp.player == P2
    assert temp.info_set() == ([1,4], [1], [1])
    #p1 infoset
    temp.construct_child()
    temp = temp.play(FORFEIT)
    assert temp.player == P2
    assert temp.info_set() == ([1, 4], [1], [1,2])

    temp = root.children[55]
    assert temp.player_pub == [1]
    assert temp.player_priv == 1
    assert temp.op_pub == [5]
    assert temp.op_priv == 4
    assert temp.player == P1

    #p1 hit
    assert temp.info_set() == ([1, 1], [5], [])
    temp.construct_child()
    temp = temp.play(HIT).children[5]
    assert temp.player == P2
    assert temp.op_pub == [1, 6]
    assert temp.info_set() == ([5,4],[1,6],[0])

    #p2hit
    #p1=[1,6,1]
    #p2=[5,4,10]
    temp.construct_child()
    temp = temp.play(HIT).children[9]
    assert temp.player == P1
    assert temp.op_pub == [5,10]
    assert temp.info_set() == ([1,6,1],[5,10],[0,0])

    #p1stand
    temp.construct_child()
    temp=temp.play(STAND)
    assert temp.player == P2
    assert temp.info_set() == ([5,10,4], [1,6], [0, 0, 1])

    #p2Hit
    temp.construct_child()
    temp = temp.play(HIT).children[0]
    assert temp.player ==P2
    assert temp.info_set()==([5,10,1,4], [1,6], [0,0,1,0])
    assert temp.terminal == False
    assert temp.game_stat == 2

    #test forfeit
    temp.construct_child()
    x = temp.play(FORFEIT)
    assert x.player == P2
    assert x.info_set() == ([5, 10, 1, 4], [1, 6], [0, 0, 1, 0, 2])
    assert x.terminal == True
#    assert x.game_stat == 3

    #test stand
    temp.construct_child()
    x = temp.play(STAND)
    assert  x.player == P2
    assert x.info_set() == ([5, 10, 1, 4], [1, 6], [0, 0, 1, 0, 1])
    assert x.terminal == True
#    assert x.game_stat == 3

    #test bust
    temp.construct_child()
    x = temp.play(HIT).children[5]
    assert x.player == P2
    assert x.info_set() == ([5,10,1,6,4],[1,6],[0,0,1,0,0])
    assert x.terminal == True
    assert x.game_stat==3

def test_cardv2():
    root = BlackJackRoot()
    temp = root.children[0]
    assert temp.player_pub == [1]
    assert temp.player_priv == 1
    assert temp.op_pub == [1]
    assert temp.op_priv == 1
    assert temp.terminal == False
    assert temp.game_stat == 1

    #player1 draw another 1
    temp.construct_child()
    temp = temp.play(HIT).children[0]
    assert temp.player==P2
    assert temp.info_set() == ([1,1], [1, 1], [0])
    assert temp.terminal == False

    #player2 stand
    temp.construct_child()

    temp = temp.play(STAND)
    assert temp.player==P1
    assert temp.game_stat == 2

    #p1 hit
    temp.construct_child()

    temp = temp.play(HIT).children[10]
    assert temp.info_set() == ([1,1,10,1], [1], [0,1,0])
    assert temp.terminal == False

    #p1 hit
    temp.construct_child()
    x = temp.play(HIT).children[7]
    assert x.info_set() == ([1, 1, 10, 8, 1], [1], [0, 1, 0,0])
    assert x.terminal == False

    #p1 hit
    temp.construct_child()

    x = temp.play(HIT).children[8]
    assert x.info_set() == ([1, 1, 10, 9, 1], [1], [0, 1, 0,0])
    assert x.terminal == True

def test_eval():
    root = BlackJackRoot()
    temp = root.children[0]
    assert temp.terminal == False
    temp.construct_child()

    #both player stand
    temp = temp.play(STAND)
    temp.construct_child()
    temp = temp.play(STAND)
    assert temp.player == P2
    assert temp.terminal == True
    assert temp.eval() == 0

    #p1 > p2
    temp = root.children[0]
    temp.construct_child()
    temp = temp.play(HIT).children[7]
    temp.construct_child()
    assert temp.player == P2
    temp = temp.play(STAND)
    temp.construct_child()
    temp = temp.play(STAND)
    assert temp.terminal == True
    assert temp.player == P1
    assert temp.eval() == 1

    #p1 < p2
    temp = root.children[0]
    temp.construct_child()
    #p1 stand
    temp = temp.play(STAND)
    temp.construct_child()
    #p2 hit
    temp = temp.play(HIT).children[7]
    temp.construct_child()
    assert temp.player == P2
    #p2 stand
    temp = temp.play(STAND)
    assert  temp.player == P2
    assert temp.eval() == 1

    #p1 bust
    temp = root.children[-1]
    assert temp.terminal == False
    temp.construct_child()
    temp = temp.play(HIT).children[1]
    #p2 turn
    assert temp.player_pub == [10]
    assert temp.player_priv == 10
    assert temp.op_pub == [10, 2]
    assert temp.op_priv == 10
    assert temp.terminal == True
    assert temp.eval()==1

    #p2 bust
    temp = root.children[-1]
    temp.construct_child()
    temp = temp.play(STAND)
    #p2 turn
    temp.construct_child()
    temp = temp.play(HIT).children[1]
    assert temp.player == P2
    assert temp.terminal == True
    assert temp.eval() == -1

    #p1 forfeit
    temp = root.children[0]
    temp.construct_child()
    temp = temp.play(FORFEIT)
    assert temp.player == P1
    assert temp.eval() == -0.5

def test_init_sigma():
    root = BlackJackRoot()
    res = init_sigma(root)