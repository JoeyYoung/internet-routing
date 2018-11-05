import numpy as np
import tensorflow as tf


class Agent:
    def __init__(self, id, paths, nei_agents):
        self.id = id
        # didn't record path to self
        self.paths = paths
        self.nei_agents = nei_agents
        self.flow_matrix = []

        # A-C basic framework
        self.actor = None
        self.critic = None

        # def action set(size:NP0*NP1*...), give the action label to use
        self.action_labels = self.init_action_label()
        self.n_actions = len(self.action_labels)
        '''
            each action is 5-dim list, store paths for flow with different destination, -1 represents self
            [p, p, p, -1, p], take id 3 e.g.     p- path in paths
            actor choose the label, agent computes the reward
        '''

    def init_action_label(self):
        action_labels = []
        if self.id is 0:
            for i in self.paths[1]:
                for j in self.paths[2]:
                    for k in self.paths[3]:
                        for m in self.paths[4]:
                            acts = []
                            acts.append(-1)  # represent this
                            acts.append(i)
                            acts.append(j)
                            acts.append(k)
                            acts.append(m)
                            action_labels.append(acts)

        if self.id is 1:
            for i in self.paths[0]:
                for j in self.paths[2]:
                    for k in self.paths[3]:
                        for m in self.paths[4]:
                            acts = []
                            acts.append(i)
                            acts.append(-1)
                            acts.append(j)
                            acts.append(k)
                            acts.append(m)
                            action_labels.append(acts)

        if self.id is 2:
            for i in self.paths[0]:
                for j in self.paths[1]:
                    for k in self.paths[3]:
                        for m in self.paths[4]:
                            acts = []
                            acts.append(i)
                            acts.append(j)
                            acts.append(-1)  # represent this
                            acts.append(k)
                            acts.append(m)
                            action_labels.append(acts)

        if self.id is 3:
            for i in self.paths[0]:
                for j in self.paths[1]:
                    for k in self.paths[2]:
                        for m in self.paths[4]:
                            acts = []
                            acts.append(i)
                            acts.append(j)
                            acts.append(k)
                            acts.append(-1)  # represent this
                            acts.append(m)
                            action_labels.append(acts)

        if self.id is 4:
            for i in self.paths[0]:
                for j in self.paths[1]:
                    for k in self.paths[2]:
                        for m in self.paths[3]:
                            acts = []
                            acts.append(i)
                            acts.append(j)
                            acts.append(k)
                            acts.append(m)
                            acts.append(-1)  # represent this
                            action_labels.append(acts)
        return action_labels

    def set_rl_setting(self, actor, critic):
        self.actor = actor
        self.critic = critic
