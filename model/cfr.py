from utils.utils import *
import numpy as np

class cfr:
    def __init__(self, root, sigma, cumulative_regret, cumulative_sigma, optimum_strategy):
        self.root = root
        self.sigma = sigma
        self.cumulative_regret = cumulative_regret
        self.cumulative_sigma = cumulative_sigma
        self.optimum_strategy = optimum_strategy
        self.expeced_util=[]

    def train(self, iterations):
        for i in range(0, iterations):
            self._compute_utility(self.root, 1, 1)
            self._update_sigma(self.root)
            self.get_optimum(self.root)
            x = self.compute_reward(self.root)
            print(i, x)
            self.expeced_util.append(x)

    def _compute_utility(self, state, pi_a, pi_b):
        children_state_utilities = {}
        if state.is_terminal():
            #print("in terminal", state.info_set(), state.eval(), state.player_pub+[state.player_priv], state.op_pub+[state.op_priv])
            return state.eval()
        if state.is_chance():
            return state.chance_prob() * sum([self._compute_utility(child, pi_a, pi_b) for child in state.children])
        utility = 0.
        for action in ACTIONS:
            state.construct_child()
           # print(state.info_set(), self.sigma[state.info_set()])
            c_pi_a = pi_a *(self.sigma[state.info_set()][action] if state.player == P1 else 1)
            c_pi_b = pi_b *(self.sigma[state.info_set()][action] if state.player == -P1 else 1)
            #print(self.sigma[state.info_set()][action])
            child_state_utility = self._compute_utility(state.play(action), c_pi_a, c_pi_b)
            #print("\t**", state.info_set(), action, child_state_utility, "**")
            utility += self.sigma[state.info_set()][action]*child_state_utility
            #print("\t\t", state.info_set(), action, value, child_state_utility, self.sigma[state.info_set()])
            children_state_utilities[action] = child_state_utility
        #print("**", state.info_set(), children_state_utilities, state.player)

        (cfr_reach, reach) = (pi_b, pi_a) if state.player == P1 else (pi_a, pi_b)
        for action in ACTIONS:
            regret =  state.player * cfr_reach *(children_state_utilities[action] - utility)
            #print(action_cfr_regret)
            #print(state.info_set(), state.player, (cfr_reach, reach), children_state_utilities[action], action_cfr_regret)
            self.cumulative_regret[state.info_set()][action] = np.max([self.cumulative_regret[state.info_set()][action]+regret, 0])
            #self.cumulative_regret[state.info_set()][action] += regret
            self.cumulative_sigma[state.info_set()][action] += reach*self.sigma[state.info_set()][action]
        return utility

    def _update_sigma(self, node):
        if node.is_terminal():
            return
        if not node.is_chance():
            node.construct_child()
            self._sigma_helper(node.info_set())
        for k in node.children:
            self._update_sigma(k)

    def _sigma_helper(self, i):
        rgrt_sum = sum(filter(lambda x : x>0, self.cumulative_regret[i].values()))
        for a in self.cumulative_regret[i]:
            self.sigma[i][a] = max(self.cumulative_regret[i][a], 0.) / rgrt_sum if rgrt_sum > 0 else 1. / len(self.cumulative_regret[i].keys())


    def get_optimum(self, node):
        if node.is_chance():
            #print(node.info_set(), node.deck, len(node.children))
            self.optimum_strategy[node.info_set()] = {a:node.chance_prob() for a in range(len(node.children))}
        else:
            node.construct_child()
            sigma_sum = sum(self.cumulative_sigma[node.info_set()].values())
            self.optimum_strategy[node.info_set()] = {a: self.cumulative_sigma[node.info_set()][a] / sigma_sum if sigma_sum > 0 else 1./len(self.cumulative_sigma[node.info_set()].keys()) for a in ACTIONS}

        for child in node.children:
            if not child.is_terminal():
                self.get_optimum(child)


    def compute_reward(self, node):
        value = 0.
        if node.is_terminal():
            return node.eval()
        if not node.is_chance():
            node.construct_child()
        for child in range(len(node.children)):
            #print(node.info_set(), child, len(node.children), self.nash_equilibrium[node.info_set()], node.deck)
            value += self.optimum_strategy[node.info_set()][child] * self.compute_reward(node.children[child])
        return value