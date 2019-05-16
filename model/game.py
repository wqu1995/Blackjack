from utils.utils import *
import random

class Card:
    def __init__(self, val, num):
        self.val = val
        self.num = num

class GameStateBase:
    def __init__(self, parent, player, game_stat):
        self.parent = parent
        self.player = player
        self.game_stat = game_stat #1 = on going 2 = one player stand 3 = end
        self.deck = []
        #self.deck = deck
        #self.actions = actions

    def play(self, action):
        return self.children[action]

    def is_chance(self):
        return self.player == CHANCE


class BlackJackRoot(GameStateBase):
    def __init__(self):
        super().__init__(parent=None, player=CHANCE, game_stat=1)
        self.children=[]
        for pc1 in deck:
            for pc2 in deck:
                for oc1 in deck:
                    for oc2 in deck:
                        temp = BlackJackPlayerState(
                            self,
                            self.game_stat,
                            P1,
                            [],
                            [pc1], pc2,
                            [oc1], oc2
                        )
                        self.children.append(temp)
        self._chance_prob = 1. / len(self.children)
        self._info_set = (0)

    def is_terminal(self):
        return False

    def info_set(self):
        return self._info_set

    def chance_prob(self):
        return self._chance_prob

    def sample_one(self):
        return random.choice(self.children)

    def is_chance(self):
        return True

class BlackJackHitState(GameStateBase):
    def __init__(self, parent, game_stat,  player, action_history, player_pub, player_priv, op_pub, op_priv):
        super().__init__(parent=parent, player=CHANCE, game_stat=game_stat)
        self.children=[]
        #self.deck = deck
        # for card in range(len(self.deck)):
        #     print(card, self.deck[card])
        #for card in range(len(self.deck)):
        for card in deck:
            if self.game_stat == 2:
                #if self.deck[card] > 0:
                    #self.deck[card] -=1
                    self.children.append(BlackJackPlayerState(
                        self,
                        self.game_stat,
                        #list(self.deck),
                        player,
                        action_history,
                        player_pub+[card], player_priv,
                        op_pub, op_priv
                    ))
                    #self.deck[card] +=1
            else:
                # if is_bust(player_pub+[card]+[player_priv]):
                #     self.children.append(BlackJackPlayerState(
                #         self,
                #         self.game_stat,
                #         player,
                #         action_history,
                #         player_pub + [card], player_priv,
                #         op_pub, op_priv
                #     ))
                # else:
                #if self.deck[card] > 0:
                    #self.deck[card] -=1
                    self.children.append(BlackJackPlayerState(
                        self,
                        self.game_stat,
                        #list(self.deck),
                        -player,
                        action_history,
                        op_pub, op_priv,
                        player_pub + [card], player_priv,
                        ))
                    #self.deck[card]+=1
        self._chance_prob = 1./len(self.children)
        self._info_set = (tuple(player_pub + [player_priv]), tuple(op_pub), tuple(action_history), (1))

    def is_terminal(self):
        return False

    def chance_prob(self):
        return self._chance_prob
    def info_set(self):
        return self._info_set
    def sample_one(self):
        return random.choice(self.children)

    def is_chance(self):
        return True


class BlackJackPlayerState(GameStateBase):
    def __init__(self, parent, game_stat, player, action_history, player_pub, player_priv, op_pub, op_priv):
        super().__init__(parent=parent, player=player, game_stat=game_stat)

        #self.deck = deck

        self.action_history = action_history
        self.player_pub = player_pub
        self.player_priv = player_priv
        self.op_pub = op_pub
        self.op_priv = op_priv
        self.terminal = self.eval_terminal()
        self._info_set = (tuple(self.player_pub+[self.player_priv]), tuple(self.op_pub), tuple(self.action_history))
        #self._info_set = ".{0}.{1}.{2}".format(' '.join(self.player_pub+[self.player_priv]), self.op_pub, ".".join(self.action_history))
        #self.children = self.construct_child()

    def eval_terminal(self):
        if not self.action_history:
            return False
        #last action forfeit
        if self.action_history[-1] == FORFEIT:
            #self.game_stat = 3
            return True
        #last action stand
        if self.action_history[-1] == STAND:
            #both player stands
            if self.game_stat==2:
                #self.game_stat = 3
                return True
            else:
                self.game_stat = 2
                return False
        else:
            if is_bust(self.player_pub+[self.player_priv]):
                self.game_stat = 3
                return True
            elif is_bust(self.op_pub+[self.op_priv]):
                self.game_stat = 4
                return True
            else:
                return False
    def play(self, action):
        return self.children[action]

    def construct_child(self):
        self.children = []
        #hit

        self.children.append(BlackJackHitState(
            self, self.game_stat,
            #list(self.deck),
            self.player,
            self.action_history+[HIT],
            self.player_pub, self.player_priv,
            self.op_pub, self.op_priv
        ))
        #stand
        #todo: change it to terminate state
        if self.game_stat==2:
            self.children.append(BlackJackPlayerState(
                self, self.game_stat,
                #list(self.deck),
                self.player,
                self.action_history+[STAND],
                self.player_pub, self.player_priv,
                self.op_pub, self.op_priv
            ))
        else:
            self.children.append(BlackJackPlayerState(
                self, self.game_stat,
                #list(self.deck),
                -self.player,
                self.action_history + [STAND],
                self.op_pub, self.op_priv,
                self.player_pub, self.player_priv
            ))
        #forfeit
        self.children.append(BlackJackPlayerState(
            self, self.game_stat,
            #list(self.deck),
            self.player,
            self.action_history + [FORFEIT],
            self.player_pub, self.player_priv,
            self.op_pub, self.op_priv
        ))

    def is_terminal(self):
        return self.terminal

    def info_set(self):
        return self._info_set

    def eval(self):
        if self.terminal == False:
            raise RuntimeError("Not terminal state!")
        if self.action_history[-1] == FORFEIT:
            if(self.player== P1):
                return -0.5
            else:
                return 0.5
        #bust
        if self.game_stat == 3:
            if self.player == P1:
                return -1
            else:
                return 1
        if self.game_stat == 4:
            if self.player == P1:
                return 1
            else:
                return -1
        if self.player==P1:
            return cmp(self.player_pub+[self.player_priv], self.op_pub+[self.op_priv])
        else:
            return -cmp(self.player_pub+[self.player_priv], self.op_pub+[self.op_priv])

