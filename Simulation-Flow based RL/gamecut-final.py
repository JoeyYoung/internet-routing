"""
    Cut down action space,
    focus on each flow to choose action (next-hop)
"""

from generator import MiniGenerator
from actor import Actor
from critic import Critic
import tensorflow as tf
import numpy as np
import collections
import random


class Game:
    def __init__(self):
        # Internet topology
        self.generator = MiniGenerator(10, 2)
        self.generator.build_topology()
        self.generator.build_directed_matrix()

        self.RLs = self.generator.Ts + self.generator.Cs + self.generator.Ms + self.generator.CPs
        self.N = 12
        self.Ns = self.generator.Ts + self.generator.Ms + self.generator.CPs + self.generator.Cs

        self.MAX = 100000
        self.ids = self.generator.ids

        self.TF = collections.defaultdict(dict)
        self.tf_num = 10
        self.TF[6][9] = 1
        self.TF[6][10] = 1
        self.TF[7][4] = 1
        self.TF[7][5] = 1
        self.TF[8][10] = 1
        self.TF[8][11] = 1
        self.TF[0][9] = 1
        self.TF[1][11] = 1
        self.TF[2][5] = 1
        self.TF[3][4] = 1

        # self.TF[9][6] = 1
        # self.TF[10][6] = 1
        # self.TF[4][7] = 1
        # self.TF[5][7] = 1
        # self.TF[10][8] = 1
        # self.TF[11][8] = 1
        # self.TF[9][0] = 1
        # self.TF[11][1] = 1
        # self.TF[5][2] = 1
        # self.TF[4][3] = 1

        # for each agent, add [s,a,r,s'] as element. size
        self.experience_pool = collections.defaultdict(dict)
        self.pool_size = 10
        for i in range(self.tf_num):
            for j in range(self.N):
                self.experience_pool[i][j] = []

    def play_game(self):
        print("play")
        sess = tf.Session()
        print('sess')

        """
            init states for every node:
                src, dst, neighbor, e-e, others' actions
        """
        states = collections.defaultdict(list)
        for i in range(self.N):
            # add flow number
            states[i].append(0)

            # add neighbor
            for j in range(len(self.generator.matrix[i])):
                if self.generator.matrix[i][j] == 1:
                    states[i].append(100)

            # reachable end-to-end throughput (all advertised are considered here)
            node = self.ids[i]
            for d in node.table:    states[i].append(0)
            for d in node.table_peer:   states[i].append(0)
            for d in node.table_provider:   states[i].append(0)
            # TODO, consider how to combine actions

        """
            create RL module
        """
        for i in self.RLs:
            print("create mode for: " + str(i.id) + ", version -1")
            n_features = len(states[i.id])
            actor = Actor(sess, n_features, i.n_actions, i.id, -1)
            critic = Critic(sess, n_features, i.id, -1)
            i.set_rl_setting(actor, critic)
            sess.run(tf.global_variables_initializer())

        print("model created")

        """
            loop time as time epoch
        """
        TF = self.TF
        # keep updating
        actions = collections.defaultdict(dict)
        for i in range(self.tf_num):
            for j in range(self.N):
                actions[i][j] = 0

        sums = []
        for time in range(self.MAX):
            print("begin time epoch: " + str(time))
            train_state_pool = collections.defaultdict(dict)
            flow_num = 0
            sum_all = 0
            rewards = {}
            for i in TF.keys():
                for j in TF[i].keys():
                    for agent in self.Ns:
                        # store state and state'
                        train_state_pool[flow_num][agent.id] = []
                        # specific one node to one flow
                        states[agent.id][0] = flow_num
                        ss = np.array(states[agent.id])
                        pro = random.random()
                        if pro > 0.1:
                            actions[flow_num][agent.id] = agent.actor.choose_action(ss)
                        else:
                            actions[flow_num][agent.id] = random.randint(0, agent.n_actions - 1)

                        train_state_pool[flow_num][agent.id].append(ss)

                    # update states to ss_
                    states_, rewards, sum_all = self.update_state(flow_num, actions)

                    flow_num += 1
                    states = states_

            # TODO, add experience replay
            flow_num = 0
            for i in TF.keys():
                for j in TF[i].keys():
                    for agent in self.Ns:
                        ss = train_state_pool[flow_num][agent.id][0]
                        ss_ = states[agent.id]
                        ss_[0] = flow_num
                        ss_ = np.array(ss_)

                        exp = []
                        exp.append(ss)
                        exp.append(rewards[agent.id])
                        exp.append(actions[flow_num][agent.id])
                        exp.append(ss_)

                        if len(self.experience_pool[flow_num][agent.id]) < self.pool_size:
                            self.experience_pool[flow_num][agent.id].append(exp)
                        else:
                            self.experience_pool[flow_num][agent.id] = self.experience_pool[flow_num][agent.id][1:]
                            self.experience_pool[flow_num][agent.id].append(exp)

                        experience = random.choice(self.experience_pool[flow_num][agent.id])

                        s = experience[0]
                        r = experience[1]
                        a = experience[2]
                        s_ = experience[3]

                        td_error = agent.critic.learn(s, r, s_)
                        agent.actor.learn(s, a, td_error)
                    flow_num += 1

            sums.append(sum_all)
            print('cut-rl-tf10-exp: ' + str(sum_all))
            if time % 500 == 0 and time != 0:
                str1 = 'cut-final-tf10-exp-sums' + str(time) + '.txt'
                file = open(str1, 'w')
                file.write(str(sums))
                file.close()

    def update_state(self, cur_flow, actions):
        TF = self.TF
        actual_flow = collections.defaultdict(dict)
        flow_num = 0
        for i in TF.keys():
            for j in TF[i].keys():
                hop_path = []
                cur = i
                hop_path.append(self.ids[cur])
                flag = -1
                count = 0
                while cur != j:
                    count += 1
                    if count > 10:
                        print("error in hop path")
                        flag = 1
                        break
                    flag = 0
                    action = self.ids[cur].action_labels[actions[flow_num][cur]]
                    if action.get(j) is not None:
                        cur = action[j]
                        hop_path.append(self.ids[cur])
                    else:
                        flag = 1
                        print("error in hop path")
                        break
                if flag == 0:
                    actual_flow[i][j] = hop_path
                flow_num += 1

        link_load = np.zeros([self.N, self.N])
        for i in actual_flow.keys():
            for j in actual_flow[i].keys():
                path = actual_flow[i][j]
                for k in range(len(path) - 1):
                    e1 = path[k]
                    e2 = path[k + 1]
                    link_load[e1.id][e2.id] += TF[i][j]
                    link_load[e2.id][e1.id] += TF[i][j]

        # store flow information on each link
        # node1:node2:[[src,dst],[src,dst]]
        # node2:node1:[[src,dst],...]
        link_flow_records = collections.defaultdict(dict)
        for i in range(self.N):
            for j in range(self.N):
                if self.generator.matrix[i][j] == 1:
                    link_flow_records[i][j] = []
                    link_flow_records[j][i] = []

        ee_throughput = np.zeros([self.N, self.N])
        for i in actual_flow.keys():
            # input node i
            for j in actual_flow[i].keys():
                flow = [i, j]
                path = actual_flow[i][j]
                temp_min = 9999
                for k in range(len(path) - 1):
                    node1 = path[k]
                    node2 = path[k + 1]
                    # record flow 'i j' on link 'node1 node2'
                    link_flow_records[node1.id][node2.id].append(flow)
                    link_flow_records[node2.id][node1.id].append(flow)

                    ee = 100 / link_load[node1.id][node2.id]
                    if ee < temp_min:
                        temp_min = ee
                ee_throughput[i][j] = temp_min
        # ee is basic throughput for each flow, need to be increased

        link_residue = collections.defaultdict(dict)
        for i in range(self.N):
            for j in range(self.N):
                if self.generator.matrix[i][j] == 1:
                    # for link 'i j'
                    remain = 100
                    for flow in link_flow_records[i][j]:
                        remain -= ee_throughput[flow[0]][flow[1]]
                    link_residue[i][j] = remain
                    link_residue[j][i] = remain

        # TODO, increase each flow throughput, update link_residue
        for i in actual_flow.keys():
            for j in actual_flow[i].keys():
                path = actual_flow[i][j]
                temp_min = 9999
                for k in range(len(path) - 1):
                    node1 = path[k]
                    node2 = path[k + 1]
                    if link_residue[node1.id][node2.id] < temp_min:
                        temp_min = link_residue[node1.id][node2.id]
                # increase
                if temp_min == 0:
                    continue
                ee_throughput[i][j] += temp_min
                # update
                for k in range(len(path) - 1):
                    node1 = path[k]
                    node2 = path[k + 1]
                    link_residue[node1.id][node2.id] -= temp_min
                    link_residue[node2.id][node1.id] -= temp_min

        states_ = collections.defaultdict(list)
        for i in range(self.N):
            states_[i].append(cur_flow)
            for j in range(len(self.generator.matrix[i])):
                if self.generator.matrix[i][j] == 1:
                    if link_load[i][j] == 0:
                        states_[i].append(100)
                    else:
                        states_[i].append(100 / link_load[i][j])

        rewards = {}
        for agent in self.RLs:
            temp_table = collections.defaultdict(list)
            for des in agent.table:
                temp_table[des].append(0)
            for des in agent.table_peer:
                temp_table[des].append(0)
            for des in agent.table_provider:
                temp_table[des].append(0)

            sum_flow = 0
            sum_ee = 0
            for i in actual_flow.keys():
                for j in actual_flow[i].keys():
                    path = actual_flow[i][j]
                    if agent in path and agent is not path[-1]:
                        sum_flow += 1
                        sum_ee += ee_throughput[i][j]
                        temp_table[j].append(ee_throughput[i][j])
            if sum_flow == 0:
                rewards[agent.id] = 0
            else:
                rewards[agent.id] = sum_ee / sum_flow

            for i in temp_table:
                avg = sum(temp_table[i]) / len(temp_table[i])
                states_[agent.id].append(avg)

        sum_all = 0
        for i in range(self.N):
            for j in range(self.N):
                sum_all += ee_throughput[i][j]

        return states_, rewards, sum_all


cutgame = Game()
cutgame.play_game()
