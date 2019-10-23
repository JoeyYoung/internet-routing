"""
    Each time round only creates four sub-pros
    Manager variables used
"""
from generator import HugeGenerator
from actor_pro import Actor
from critic_pro import Critic
from multiprocessing import Manager
import multiprocessing
import datetime
import tensorflow as tf
import numpy as np
import collections
import random
from multiprocessing.managers import BaseManager
import time
import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "0, 1"
gpu_options = tf.GPUOptions(allow_growth=True)

agents_gpu = collections.defaultdict(list)


class Game:
    def __init__(self):
        """
            All these vars are unchanged during game
        """
        self.generator = HugeGenerator(91, 1)
        self.generator.build_topology()

        # TODO, modify this by dividing
        self.RLs = self.generator.CPs[35:]
        self.N = 92
        self.Ns = self.generator.Ts + self.generator.Ms + self.generator.CPs + self.generator.Cs

        self.MAX = 100000
        self.ids = self.generator.ids

        self.TF = collections.defaultdict(dict)
        for region in range(1, 14):
            header_cp = 14 + 6 * (region - 1)
            tail_cp = 19 + 6 * (region - 1)
            self.TF[0][header_cp] = 1
            self.TF[0][tail_cp] = 1

            nei_region = (region + 1) % 13
            if nei_region == 0:
                nei_region = 13
            header_cp_nei = 14 + 6 * (nei_region - 1)
            tail_cp_nei = 19 + 6 * (nei_region - 1)
            self.TF[header_cp + 2][header_cp_nei + 2] = 1
            self.TF[header_cp + 3][header_cp_nei + 3] = 1
            self.TF[header_cp][header_cp_nei] = 1
            self.TF[tail_cp][tail_cp_nei] = 1

        self.tf_num = 0
        for i in self.TF.keys():
            for j in self.TF[i].keys():
                self.tf_num += 1
        print("Inject " + str(self.tf_num) + " flows")

        self.global_optimal = 600
        self.episode = 0
        self.memory = None
        self.agents_gpu = collections.defaultdict(list)
        agents_gpu[0] = []
        agents_gpu[1] = []
        agents_gpu[2] = []
        agents_gpu[3] = []

        # for each agent, add [s,a,r,s'] as element. size
        self.pool_size = 16
        self.sample_size = 16
        # self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))

    def set_global_memory(self, m):
        self.memory = m

    def set_rl_agents(self):
        for i in self.RLs:
            print("create mode for: " + str(i.id) + ", version -1")
            n_features_critic = len(self.memory['states_g'][i.id])
            n_features_actor = len(self.memory['states'][i.id]) + 1

            # "0 1" 1,0
            gpu_id = (i.id + 1) % 2

            with tf.device('/gpu:%d' % gpu_id):
                actor = Actor(n_features_actor, i.n_actions, i.id, -1, i.action_labels)
                critic = Critic(n_features_critic, i.id, -1)
            self.agents_gpu[gpu_id].append(i.id)
            i.set_rl_setting(actor, critic)

        # self.sess.run(tf.global_variables_initializer())
        print("model created")

    def agent_action(self, gpu_id, s_e, e_e):
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        for aid in self.agents_gpu[gpu_id]:
            self.ids[aid].actor.set_session(sess)
        sess.run(tf.global_variables_initializer())

        while (1):
            s_e.wait()
            print("action process")
            f_num = 0
            actions_new = self.memory['actions']
            train_local_view_new = self.memory['train_local_view_%d' % gpu_id]
            train_state_pool_new = self.memory['train_state_pool_%d' % gpu_id]
            states_old = self.memory['states']
            states_g_old = self.memory['states_g']
            pro = random.random()
            for i in self.TF.keys():
                for j in self.TF[i].keys():
                    for aid in self.agents_gpu[gpu_id]:
                        local_view = np.array([f_num] + states_old[aid])
                        valida = game.ids[aid].filter[j]

                        states_g_old[aid][0] = f_num
                        ss = np.array(states_g_old[aid])

                        if pro > self.episode:
                            cnm = self.ids[aid].actor.choose_action(local_view, valida, 'prob')
                        else:
                            if -1 in valida:
                                cnm = 0
                            else:
                                cnm = self.ids[aid].action_labels.index(random.choice(valida))
                        actions_new[f_num][aid] = cnm

                        train_local_view_new[f_num][aid] = local_view
                        train_state_pool_new[f_num][aid] = ss
                    f_num += 1

            self.memory['actions'] = actions_new
            self.memory['train_local_view_%d' % gpu_id] = train_local_view_new
            self.memory['train_state_pool_%d' % gpu_id] = train_state_pool_new
            e_e.set()
            s_e.clear()

    def agent_learn(self, gpu_id, s_e, e_e):
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        for aid in self.agents_gpu[gpu_id]:
            self.ids[aid].actor.set_session(sess)
            self.ids[aid].critic.set_session(sess)
        sess.run(tf.global_variables_initializer())

        while (1):
            s_e.wait()
            print("learn process")
            f_num = 0
            states_old = self.memory['states']
            states_g_old = self.memory['states_g']
            train_local_view_old = self.memory['train_local_view_%d' % gpu_id]
            train_state_pool_old = self.memory['train_state_pool_%d' % gpu_id]
            actions_old = self.memory['actions']
            rewards_old = self.memory['rewards']
            f_a_p = self.memory['flow_actual_path']
            experience_pool_new = self.memory['experience_pool_%d' % gpu_id]

            for i in self.TF.keys():
                for j in self.TF[i].keys():
                    for aid in self.agents_gpu[gpu_id]:
                        if aid not in f_a_p[f_num][:len(f_a_p[f_num]) - 1]:
                            continue
                        # ss is useless for loc
                        ss = train_state_pool_old[f_num][aid]
                        ss_ = states_g_old[aid]
                        ss_[0] = f_num
                        ss_ = np.array(ss_)

                        ac = actions_old[f_num][aid]

                        view = train_local_view_old[f_num][aid]

                        cur_exp = [ss, ss_, ac, rewards_old[aid], view]

                        if len(experience_pool_new[aid]) < self.pool_size:
                            experience_pool_new[aid].append(cur_exp)
                        else:
                            experience_pool_new[aid] = experience_pool_new[aid][1:]
                            experience_pool_new[aid].append(cur_exp)
                            indexs_learn = np.random.choice(self.pool_size, self.sample_size)
                            # time.sleep(0.0072463)
                            for k in indexs_learn:
                                exp = experience_pool_new[aid][k]
                                td_error = self.ids[aid].critic.learn(exp[0], exp[3], exp[1])
                                self.ids[aid].actor.learn(exp[4], exp[2], td_error)
                    f_num += 1
            self.memory['experience_pool_%d' % gpu_id] = experience_pool_new
            e_e.set()
            s_e.clear()


if __name__ == '__main__':
    with tf.device('/cpu:0'):
        game = Game()

        manager = Manager()
        memory = manager.dict()

        states = collections.defaultdict(list)
        for i in range(game.N):
            for j in range(len(game.generator.matrix[i])):
                if game.generator.matrix[i][j] == 1:
                    states[i].append(0)
            node = game.ids[i]
            for d in node.table:    states[i].append(0)
            for d in node.table_peer:   states[i].append(0)
            for d in node.table_provider:   states[i].append(0)
        memory['states'] = states

        # combine others' states and last actions for each flow
        states_g = collections.defaultdict(list)
        for i in range(game.N):
            # add flow num
            states_g[i] = [0]
            # all agents' basic states
            for j in range(game.N):
                if j == i or game.generator.matrix[i][j] == 1 or game.generator.matrix[j][i] == 1:
                    states_g[i] += states[j]
            # actions of all agents for all flows
            for k in range(game.tf_num):
                for q in range(game.N):
                    if q == i or game.generator.matrix[q][i] == 1 or game.generator.matrix[i][q] == 1:
                        states_g[i].append(0)
        memory['states_g'] = states_g

        actions = collections.defaultdict(dict)
        f_num = 0
        for i in game.TF.keys():
            for j in game.TF[i].keys():
                for k in range(game.N):
                    valida = game.ids[k].filter[j]
                    if -1 in valida:
                        actions[f_num][k] = 0
                    else:
                        actions[f_num][k] = game.ids[k].action_labels.index(random.choice(valida))
                f_num += 1
        memory['actions'] = actions

        train_state_pool_0 = collections.defaultdict(dict)
        memory['train_state_pool_0'] = train_state_pool_0

        train_state_pool_1 = collections.defaultdict(dict)
        memory['train_state_pool_1'] = train_state_pool_1

        train_local_view_0 = collections.defaultdict(dict)
        memory['train_local_view_0'] = train_local_view_0

        train_local_view_1 = collections.defaultdict(dict)
        memory['train_local_view_1'] = train_local_view_1

        exp_pool_0 = collections.defaultdict(list)
        memory['experience_pool_0'] = exp_pool_0

        exp_pool_1 = collections.defaultdict(list)
        memory['experience_pool_1'] = exp_pool_1

        rewards = {}
        memory['rewards'] = rewards

        flow_actual_path = collections.defaultdict(list)
        memory['flow_actual_path'] = flow_actual_path

        game.set_global_memory(memory)
        game.set_rl_agents()

        """
            begin the game process part
            sess should in each process
            written into lock version
        """
        start_event_a0 = multiprocessing.Event()
        start_event_a1 = multiprocessing.Event()
        end_event_a0 = multiprocessing.Event()
        end_event_a1 = multiprocessing.Event()

        start_event_l0 = multiprocessing.Event()
        start_event_l1 = multiprocessing.Event()
        end_event_l0 = multiprocessing.Event()
        end_event_l1 = multiprocessing.Event()

        """
            Start action process
        """
        processes_action = []
        # gpu 0, action
        process = multiprocessing.Process(target=game.agent_action, args=(0, start_event_a0, end_event_a0))
        process.start()
        processes_action.append(process)
        # gpu 1, action
        process = multiprocessing.Process(target=game.agent_action, args=(1, start_event_a1, end_event_a1))
        process.start()
        processes_action.append(process)

        """
            Start learn process
        """
        processes_learn = []
        # gpu 0
        process = multiprocessing.Process(target=game.agent_learn, args=(0, start_event_l0, end_event_l0))
        process.start()
        processes_learn.append(process)
        # gpu 1
        process = multiprocessing.Process(target=game.agent_learn, args=(1, start_event_l1, end_event_l1))
        process.start()
        processes_learn.append(process)

        """
            Define Manager
        """
        # TODO, modify device label

        BaseManager.register('get_actions_g7_queue')
        BaseManager.register('get_rewards_g7_queue')
        BaseManager.register('get_states_g7_queue')
        BaseManager.register('get_fap_g7_queue')
        BaseManager.register('get_finish_g7_queue')
        BaseManager.register('get_actions_glb_g7_queue')
        mgr = BaseManager(address=("172.16.68.1", 4444), authkey=b"game")

        mgr.connect()
        actions_g7 = mgr.get_actions_g7_queue()
        rewards_g7 = mgr.get_rewards_g7_queue()
        states_g7 = mgr.get_states_g7_queue()
        fap_g7 = mgr.get_states_g7_queue()
        finish_g7 = mgr.get_finish_g7_queue()
        actions_glb_g7 = mgr.get_actions_glb_g7_queue()

        for time_round in range(game.MAX):
            print("time: " + str(time_round))

            """
                Action Choosing part
            """
            start_event_a0.set()
            start_event_a1.set()
            end_event_a0.wait()
            end_event_a1.wait()

            end_event_a0.clear()
            end_event_a1.clear()

            """
                give actions to master
                Receive from master to update its memory
            """
            actions_g7.put(memory['actions'])

            s = states_g7.get()
            r = rewards_g7.get()
            fap = fap_g7.get()
            g_a = actions_glb_g7.get()

            memory['rewards'] = r
            memory['states'] = s
            memory['flow_actual_path'] = fap
            memory['actions'] = g_a

            states_g_ = collections.defaultdict(list)
            for k in range(game.N):
                states_g_[k] = [0]
                for q in range(game.N):
                    if q == k or game.generator.matrix[q][k] == 1 or game.generator.matrix[k][q] == 1:
                        states_g_[k] += s[q]
                for z in g_a.keys():
                    for x in g_a[z].keys():
                        if k == x or game.generator.matrix[k][x] == 1 or game.generator.matrix[x][k] == 1:
                            states_g_[k].append(g_a[z][x])
            memory['states_g'] = states_g_

            """
                Agents learn part
            """
            start_event_l0.set()
            start_event_l1.set()
            end_event_l0.wait()
            end_event_l1.wait()

            end_event_l0.clear()
            end_event_l1.clear()

        finish_g7.put(0)
        for process in processes_action:
            process.terminate()
        for process in processes_learn:
            process.terminate()
