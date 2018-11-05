import numpy as np
import collections
import tensorflow as tf
# import matplotlib as plt
from actor import Actor
from critic import Critic
from agent import Agent


'''
    build a simple network of 5 nodes with id 0-4
    5 links connect each
    each agent has specific:
        end-to-end path set, action set, neighbor information 
'''


class NetEnv:
    def __init__(self):
        self.iteration = 10000
        self.num_agents = 5
        self.num_links = 5
        self.agents = []
        self.STEP = 50
        self.MAX = 3000

        # store the connection information and link capacity
        # can be modified to some special cases
        self.links = np.zeros([5, 5])
        self.links[0][1] = self.links[1][0] = 100
        self.links[1][2] = self.links[2][1] = 40
        self.links[1][3] = self.links[3][1] = 80
        self.links[2][3] = self.links[3][2] = 30
        self.links[3][4] = self.links[4][3] = 100

        # get the potential paths to forward
        paths_0, paths_1, paths_2, paths_3, paths_4 = self.init_path()

        # get local neighbor view for each agent
        self.agents.append(Agent(id=0, paths=paths_0, nei_agents=[1]))
        self.agents.append(Agent(id=1, paths=paths_1, nei_agents=[0, 2, 3]))
        self.agents.append(Agent(id=2, paths=paths_2, nei_agents=[1, 3]))
        self.agents.append(Agent(id=3, paths=paths_3, nei_agents=[1, 2, 4]))
        self.agents.append(Agent(id=4, paths=paths_4, nei_agents=[3]))

    @staticmethod
    def init_path():
        paths_0 = collections.defaultdict(list)
        paths_0[1].append([0, 1])
        paths_0[2].append([0, 1, 2])
        paths_0[2].append([0, 1, 3, 2])
        paths_0[3].append([0, 1, 3])
        paths_0[3].append([0, 1, 2, 3])
        paths_0[4].append([0, 1, 3, 4])
        paths_0[4].append([0, 1, 2, 3, 4])

        paths_1 = collections.defaultdict(list)
        paths_1[0].append([1, 0])
        paths_1[2].append([1, 2])
        paths_1[2].append([1, 3, 2])
        paths_1[3].append([1, 3])
        paths_1[3].append([1, 2, 3])
        paths_1[4].append([1, 3, 4])
        paths_1[4].append([1, 2, 3, 4])

        paths_2 = collections.defaultdict(list)
        paths_2[0].append([2, 1, 0])
        paths_2[0].append([2, 3, 1, 0])
        paths_2[1].append([2, 1])
        paths_2[1].append([2, 3, 1])
        paths_2[3].append([2, 3])
        paths_2[3].append([2, 1, 3])
        paths_2[4].append([2, 3, 4])
        paths_2[4].append([2, 1, 3, 4])

        paths_3 = collections.defaultdict(list)
        paths_3[0].append([3, 1, 0])
        paths_3[0].append([3, 2, 1, 0])
        paths_3[1].append([3, 1])
        paths_3[1].append([3, 2, 1])
        paths_3[2].append([3, 2])
        paths_3[2].append([3, 1, 2])
        paths_3[4].append([3, 4])

        paths_4 = collections.defaultdict(list)
        paths_4[0].append([4, 3, 1, 0])
        paths_4[0].append([4, 3, 2, 1, 0])
        paths_4[1].append([4, 3, 1])
        paths_4[1].append([4, 3, 2, 1])
        paths_4[2].append([4, 3, 2])
        paths_4[2].append([4, 3, 1, 2])
        paths_4[3].append([4, 3])

        return paths_0, paths_1, paths_2, paths_3, paths_4

    def play_game(self):
        sess = tf.Session()
        # init_state, s for each agent
        states = collections.defaultdict(list)
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if self.links[i][j] != 0:
                    # add neighbor e-e (init capacity)
                    states[i].append(self.links[i][j])
            # add des-path e-e, init e-e is unknown, all det as dim
            for m in range(4):
                states[i].append(0)

        # create AC model, bind to each agent
        for q in range(self.num_agents):
            agent = self.agents[q]
            # get the state features for each agent
            n_features = 0
            for w in range(self.num_agents):
                if self.links[q][w] != 0:
                    n_features += 1
            n_features += 4
            actor = Actor(sess, n_features, agent.n_actions, q)
            critic = Critic(sess, n_features, q)
            agent.set_rl_setting(actor, critic)
            sess.run(tf.global_variables_initializer())

        '''
            loop time as time epoch
        '''
        sum_reward_ = 0
        r0 = 0
        r1 = 0
        r2 = 0
        r3 = 0
        r4 = 0
        results = []
        result_0 = []
        result_1 = []
        result_2 = []
        result_3 = []
        result_4 = []
        for t in range(self.MAX):
            # randomly generate flow matrix for each agent
            for i in range(self.num_agents):
                self.agents[i].flow_matrix = np.random.randint(0, 2, [5, 5])
                # avoid flow with same source and destination
                for j in range(self.num_agents):
                    if self.agents[i].flow_matrix[j][j] == 1:
                        self.agents[i].flow_matrix[j][j] = 0

            # every agent takes the action, here is the label set
            actions = []
            for agent in self.agents:
                s = np.array(states[agent.id])
                actions.append(agent.actor.choose_action(s))

            '''
                get the reward: based on actions(others) and flow matrix(othersb)
                actual flow: id-det-path
                n_flow: id-det-number
                link_load: assign capacity
            '''
            actual_flow = collections.defaultdict(dict)
            n_flow = collections.defaultdict(dict)
            for i in range(self.num_agents):
                agent = self.agents[i]
                # thing about this agent's actual flow, for each destination
                action = agent.action_labels[actions[i]]
                for j in range(5):
                    if action[j] == -1:
                        actual_flow[i][j] = 0
                    else:
                        actual_flow[i][j] = action[j]
                # use flow_matrix as filter
                for u in range(5):
                    n_flow[i][u] = 0
                    if u == i: continue
                    for v in range(5):
                        if agent.flow_matrix[v][u] == 1:
                            n_flow[i][u] += 1
                    if n_flow[i][u] == 0:
                        actual_flow[i][u] = 0

            # computer link_load of each link
            link_load = {}
            link_load[1] = 0  # 0-1
            link_load[3] = 0  # 1-2
            link_load[4] = 0  # 1-3
            link_load[5] = 0  # 2-3
            link_load[7] = 0  # 3-4
            for i in range(self.num_agents):
                for j in range(5):
                    path = actual_flow[i][j]
                    # has flow traffic, add the link load
                    if path != 0:
                        for k in range(len(path) - 1):
                            key = path[k] + path[k + 1]
                            link_load[key] += 1

            # compute the throughput for each 'agent to destination':
            # id-dst-throughput
            end_end_throughputs = collections.defaultdict(dict)
            for i in range(self.num_agents):
                for j in range(5):
                    if actual_flow[i][j] == 0: continue
                    flow_path = actual_flow[i][j]
                    throughput = 9999
                    for k in range(len(flow_path) - 1):
                        key = flow_path[k] + flow_path[k + 1]
                        if self.links[k][k + 1] / link_load[key] < throughput:
                            throughput = self.links[k][k + 1] / link_load[key]
                    end_end_throughputs[i][j] = throughput

            # calculate the reward for each agent
            rewards = []

            for i in range(self.num_agents):
                agent = self.agents[i]
                sum = 0
                number = 0
                for j in range(5):
                    if n_flow[i][j] == 0: continue
                    number += n_flow[i][j]
                    sum += n_flow[i][j] * end_end_throughputs[i][j]
                if number == 0:
                    rewards.append(0)
                else:
                    reward = sum / number
                    rewards.append(reward)

            # calculate the sum of end-to-end throughput
            if t % self.STEP == 0:
                # print 'time epoch: ', t, ' mean_sum_reward: ', sum_reward_ / self.STEP
                print 'agent0: ', r0 / self.STEP, ' agent1: ', r1 / self.STEP, ' agent2: ', r2 / self.STEP, ' agent3: ', r3 /self.STEP, ' agent4: ', r4 / self.STEP
                result_0.append(r0/self.STEP)
                result_1.append(r1/self.STEP)
                result_2.append(r2/self.STEP)
                result_3.append(r3/self.STEP)
                result_4.append(r4/self.STEP)
                # results.append(sum_reward_/self.STEP)
                sum_reward_ = 0
                r0 = 0
                r1 = 0
                r2 = 0
                r3 = 0
                r4 = 0

            sum_reward = 0
            for i in range(5):
                r0 += rewards[0]
                r1 += rewards[1]
                r2 += rewards[2]
                r3 += rewards[3]
                r4 += rewards[4]
                for j in range(5):
                    if end_end_throughputs[i].get(j) is None: continue
                    sum_reward += end_end_throughputs[i][j]
            sum_reward_ += sum_reward

            # step into next state s_:, based on actions
            # update not only the end-to-end throughput, but also neighbor throughput
            states_ = collections.defaultdict(list)
            for i in range(self.num_agents):
                for j in range(self.num_agents):
                    if self.links[i][j] != 0:
                        # need to calculate directly link neighbor throughput
                        key = i + j
                        states_[i].append(self.links[i][j] / link_load[key])
                for m in range(5):
                    # add all end-to-end observed, but 4 dim
                    if i == m: continue
                    # i-m can't be observed
                    if end_end_throughputs[i].get(m) is None:
                        states_[i].append(0)
                    else:
                        states_[i].append(end_end_throughputs[i][m])

            # critic learn, get td_error
            # actor learn
            for i in range(self.num_agents):
                agent = self.agents[i]
                s = np.array(states[i])
                r = rewards[i]
                s_ = np.array(states_[i])
                td_error = agent.critic.learn(s, r, s_)
                a = actions[i]
                agent.actor.learn(s, a, td_error)

            # s = s_ , needs modify the states
            states = states_

        print result_0
        print result_1
        print result_2
        print result_3
        print result_4

net = NetEnv()
net.play_game()
