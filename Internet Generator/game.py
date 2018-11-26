from generator import Generator
from actor import Actor
from critic import Critic
import tensorflow as tf
import collections


class Game:
    def __init__(self):
        # Internet topology
        self.generator = Generator(1000, 4)
        self.generator.build_topology()
        self.Ns = self.generator.Ts + self.generator.Ms + self.generator.CPs + self.generator.Cs
        # output setting
        self.STEP = 5
        self.MAX = 1000

        # TODO, apply TF traffic
        # TODO, apply link capacity(all 100?)

    def play_game(self):
        sess = tf.Session()

        # init states, add neigh-dim
        # order in states is important
        states = collections.defaultdict(list)
        for t in self.generator.Ts:
            for t_customer in t.customers_C:
                states[t.id].append(100)
            for t_customer in t.customers_CP:
                states[t.id].append(100)
            for t_customer in t.customers_M:
                states[t.id].append(100)
            for t_peer in t.peers_T:
                states[t.id].append(100)

            # reachable end-to-end throughput (all advertised are considered here)
            for destination in t.table:
                states[t.id].append(0)
            for destination in t.table:
                states[t.id].append(0)

        # create AC-model, define action set
        for i in self.Ns:
            # node i
            n_features = len(states[i.id])
            actor = Actor(sess, n_features, i.n_actions, i.id)
            critic = Critic(sess, n_features, i.id)
            i.set_rl_setting(actor, critic)
            sess.run(tf.global_variables_initializer())

        '''
            loop time as time epoch
        '''


game = Game()
game.play_game()
