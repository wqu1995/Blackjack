from model.game import *
from model.cfr import *
import matplotlib.pyplot as plt

sigma = dict()
cumulative_regret = dict()
cumulative_sigma = dict()
optimum_strategy = dict()

def init(node):
    if not node.is_chance():
        #print(node.info_set())
        #print("\t", node.player_pub + [node.player_priv], node.op_pub + [node.op_priv])
        node.construct_child()
        sigma[node.info_set()] = {child: 1./len(node.children) for child in ACTIONS}
        cumulative_regret[node.info_set()] = {child: 0 for child in ACTIONS}
        cumulative_sigma[node.info_set()] = {child: 0 for child in ACTIONS}
        optimum_strategy[node.info_set()] = {child: 0 for child in ACTIONS}
    else:
        #sigma[node.info_set()] = {child: 1./len(node.children) for child in range(len(node.children))}
        cumulative_regret[node.info_set()] = {child: 0 for child in range(len(node.children))}
        cumulative_sigma[node.info_set()] = {child: 0 for child in range(len(node.children))}
        optimum_strategy[node.info_set()] = {child: 0 for child in range(len(node.children))}

    for child in node.children:
        if not child.is_terminal():
            init(child)

def main():
    root = BlackJackRoot()
    init(root)
    print(len(sigma))
    trainer = cfr(root, sigma, cumulative_regret, cumulative_sigma, optimum_strategy)
    trainer.train(iterations=100)
    plt.plot(range(100), trainer.expeced_util)
    plt.xlabel('Iteration')
    plt.ylabel('Expected Utility')
    plt.legend("CFR")
    plt.show()
    print("**********************************************************")
    # for k, v in sigma.items():
    #     print(k, v)


if __name__ == "__main__":
    main()