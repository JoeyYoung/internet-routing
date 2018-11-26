import numpy as np
import random
import collections
import tensorflow as tf
import matplotlib.pyplot as plt
from agent import Agent
from actor import Actor
from critic import Critic


class NetEnv:
    def __init__(self):
        self.num_agents = 5
        self.num_links = 5  # seems useless
        self.agents = []
        self.STEP = 5
        self.MAX = 1000

        # store the connection information and link capacity
        # can be modified to some special cases
        self.links = np.zeros([5, 5])
        # define the links, capacity
        self.links[0][1] = self.links[1][0] = 80
        self.links[0][2] = self.links[2][0] = 100
        self.links[1][3] = self.links[3][1] = 120
        self.links[2][4] = self.links[4][2] = 80
        self.links[3][4] = self.links[4][3] = 120
        # TODO, back
        self.links[1][4] = self.links[4][1] = 80

        # TODO traffic matrix, try different scale
        self.TF = np.zeros([5, 5])
        self.TF[0][4] = 1
        self.TF[2][4] = 1
        # self.TF[1][4] = 1
        self.TF[1][3] = 1
        # self.TF[2][1] = 1

        # set BGP paths for each agent
        paths_0, paths_1, paths_2, paths_3, paths_4 = self.init_path()
        self.agents.append(Agent(id=0, paths=paths_0))
        self.agents.append(Agent(id=1, paths=paths_1))
        self.agents.append(Agent(id=2, paths=paths_2))
        self.agents.append(Agent(id=3, paths=paths_3))
        self.agents.append(Agent(id=4, paths=paths_4))

    # path_id[destination]:[path], no self index
    # only agent 0 multi action
    @staticmethod
    def init_path():
        paths_0 = collections.defaultdict(list)
        paths_0[1].append([0, 1])
        paths_0[2].append([0, 2])
        paths_0[3].append([0, 1, 3])
        # paths_0[3].append([0, 2, 4, 3])
        # TODO, back
        # paths_0[3].append([0, 1, 4, 3])
        paths_0[4].append([0, 2, 4])
        paths_0[4].append([0, 1, 3, 4])
        # TODO, back
        paths_0[4].append([0, 1, 4])

        paths_1 = collections.defaultdict(list)
        paths_1[0].append([1, 0])
        paths_1[2].append([1, 0, 2])
        paths_1[3].append([1, 3])
        # TODO, back
        # paths_1[3].append([1, 4, 3])
        paths_1[4].append([1, 3, 4])
        # TODO, back
        paths_1[4].append([1, 4])

        paths_2 = collections.defaultdict(list)
        paths_2[0].append([2, 0])
        paths_2[1].append([2, 0, 1])
        paths_2[3].append([2, 4, 3])
        paths_2[4].append([2, 4])

        paths_3 = collections.defaultdict(list)
        paths_3[0].append([3, 1, 0])
        paths_3[1].append([3, 1])
        paths_3[2].append([3, 1, 2, 0])
        paths_3[4].append([3, 4])

        paths_4 = collections.defaultdict(list)
        paths_4[0].append([4, 2, 0])
        paths_4[1].append([4, 2, 0, 1])
        paths_4[2].append([4, 2])
        paths_4[3].append([4, 3])

        return paths_0, paths_1, paths_2, paths_3, paths_4

    def play_game(self):
        sess = tf.Session()

        # init state, for each agent: add neighbor-dim(capacity), obtained e-e(4 dim fixed, no self),
        # id: []
        states = collections.defaultdict(list)
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if self.links[i][j] != 0:
                    states[i].append(self.links[i][j])
            for m in range(4):
                states[i].append(0)

        # create AC-model, define action set(Actor class)
        for i in range(self.num_agents):
            agent = self.agents[i]
            n_features = 0
            for j in range(self.num_agents):
                if self.links[i][j] != 0:
                    n_features += 1
            n_features += 4
            actor = Actor(sess, n_features, agent.n_actions, i)
            critic = Critic(sess, n_features, i)
            agent.set_rl_setting(actor, critic)
            sess.run(tf.global_variables_initializer())

        '''
            loop time as time epoch
        '''
        r0 = 0
        r2 = 0
        r1 = 0
        r0_a = []
        r2_a = []
        r1_a = []
        for t in range(self.MAX):
            # begin with state, every agent takes the action
            # index is id
            actions = []
            for i in range(self.num_agents):
                agent = self.agents[i]
                s = np.array(states[i])
                actions.append(agent.actor.choose_action(s))

            '''
                get the reward, based on TF and actions
                from the view of each agent:
                    get the actual flows information, *path* (to get the link load - n)
                    obtained e-e
                give clues to next state
            '''
            # TODO think about the actual flow: by-passing domain
            actual_flow = collections.defaultdict(dict)
            for i in range(self.num_agents):
                agent = self.agents[i]
                # transfer action label to actual action path
                action = agent.action_labels[actions[i]]
                for j in range(5):
                    # use TF as filter
                    if action[j] == -1 or self.TF[i][j] == 0:
                        actual_flow[i][j] = 0
                    else:
                        actual_flow[i][j] = action[j]

            # computer the link load of each link
            link_load = {}
            link_load[1] = 0  # 0-1
            link_load[2] = 0  # 0-2
            link_load[4] = 0  # 1-3
            # TODO, back
            link_load[5] = 0  # 1-4
            link_load[6] = 0  # 2-4
            link_load[7] = 0  # 3-4

            for i in range(self.num_agents):
                for j in range(5):
                    path = actual_flow[i][j]
                    # has flow traffic, add the link load
                    if path != 0:
                        for k in range(len(path) - 1):
                            key = path[k] + path[k + 1]
                            link_load[key] += 1

            # TODO use more general way, add correct noisy
            # computer the throughput for each link
            # the end-to-end throughput for a path is to choose the minimum T value
            # 0-represent no flow pass
            throughputs = {}
            if link_load[1] != 0:
                throughputs[1] = self.links[0][1] / link_load[1]
            else:
                throughputs[1] = 0  # not observed
            throughputs[1] += random.randint(-2, 2)
            if link_load[2] != 0:
                throughputs[2] = self.links[0][2] / link_load[2]
            else:
                throughputs[2] = 0
            throughputs[2] += random.randint(-2, 2)
            if link_load[4] != 0:
                throughputs[4] = self.links[1][3] / link_load[4]
            else:
                throughputs[4] = 0
            throughputs[4] += random.randint(-2, 2)
            # TODO, back
            if link_load[5] != 0:
                throughputs[5] = self.links[1][4] / link_load[5]
            else:
                throughputs[5] = 0
            throughputs[5] += random.randint(-2, 2)
            if link_load[6] != 0:
                throughputs[6] = self.links[2][4] / link_load[6]
            else:
                throughputs[6] = 0
            throughputs[6] += random.randint(-2, 2)
            if link_load[7] != 0:
                throughputs[7] = self.links[3][4] / link_load[7]
            else:
                throughputs[7] = 0
            throughputs[7] += random.randint(-2, 2)

            '''
                get the reward for each agent
            '''
            # consider average throughput as by-passing
            # forwards- id: dst: path/ transfer tasks for each agent
            forwards = collections.defaultdict(dict)
            for i in range(self.num_agents):
                agent = self.agents[i]
                # get every flow path
                for m in range(5):
                    for n in range(5):
                        path = actual_flow[m][n]
                        if path == 0: continue
                        for p in path:
                            # agent i as by-passing
                            if i == p and path.index(p) != len(path) - 1:
                                forwards[i][path[len(path) - 1]] = path[path.index(p):]

            # TODO, bug: when no actual flow, there will be no reward for index(agent id)
            # TODO, however, agent0/1/2 are sure to have flow
            rewards = {}
            ee_throughputs = collections.defaultdict(dict)
            for i in range(self.num_agents):
                # no transfer tasks
                if forwards.get(i) is None: continue
                sum_t = 0
                for key in forwards[i]:
                    # calculate end-to-end
                    path = forwards[i][key]
                    temp_min = 9999
                    for k in range(len(path) - 1):
                        v = path[k] + path[k + 1]
                        if throughputs[v] < temp_min:
                            temp_min = throughputs[v]
                    ee_throughputs[i][key] = temp_min
                    sum_t += temp_min
                rewards[i] = sum_t / len(forwards[i])
            print rewards[0]

            # print 'time_epoch ', t, ': ', 'agent0 :', rewards[0]
            # print 'time_epoch ', t, ': ', 'agent2 :', rewards[2]

            # step into next state
            states_ = collections.defaultdict(list)
            for i in range(self.num_agents):
                for j in range(self.num_agents):
                    if self.links[i][j] != 0:
                        key = i + j
                        states_[i].append(throughputs[key])
                for m in range(5):
                    if i == m: continue
                    if ee_throughputs.get(i) is None or ee_throughputs[i].get(m) is None:
                        states_[i].append(0)
                    else:
                        states_[i].append(ee_throughputs[i][m])

            # learn
            # TODO, back, index error, problems in rewards, here for 0,1,2
            for i in range(self.num_agents - 2):
                agent = self.agents[i]
                s = np.array(states[i])
                r = rewards[i]
                s_ = np.array(states_[i])
                td_error = agent.critic.learn(s, r, s_)
                a = actions[i]
                agent.actor.learn(s, a, td_error)

            states = states_

            # TODO STEP THE DATA, AND DRAW
            # TODO DO MORE TEST, MORE FLOWS
            r0 += rewards[0]
            r2 += rewards[2]
            r1 += rewards[1]
            if t % self.STEP == 0:
                r0_a.append(r0 / self.STEP)
                r2_a.append(r2 / self.STEP)
                r1_a.append(r1 / self.STEP)
                r0 = r2 = r1 = 0

        # TODO DRAW
        times = []
        for i in range(self.MAX):
            if i % self.STEP == 0 and i != 0:
                times.append(i)

        # draw agent 0/2
        plt.plot(times[1:], r0_a[1:len(r0_a) - 1], label='agent0')
        plt.plot(times[1:], r2_a[1:len(r2_a) - 1], label='agent2')
        plt.plot(times[1:], r1_a[1:len(r1_a) - 1], 'r', label='agent1')
        plt.legend(loc=0)
        plt.xlabel('time round')
        plt.ylabel('average throughput')

        plt.show()

        # draw agent 1/3
        # plt.plot(times[1:], r1_a[1:len(r0_a) - 1], 'r', label='agent1')
        # plt.legend(loc=0)
        # plt.xlabel('time round')
        # plt.ylabel('average throughput')
        #
        # plt.show()


Net = NetEnv()
Net.play_game()
