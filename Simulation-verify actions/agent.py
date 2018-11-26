import numpy as np


class Agent:
    def __init__(self, id, paths):
        self.id = id
        self.paths = paths

        # A-C basic framework
        self.actor = None
        self.critic = None

        self.action_labels = self.init_action_label()
        self.n_actions = len(self.action_labels)

    #  TODO redefine labels, index is label, element is action vector for differ-dst flows
    def init_action_label(self):
        action_labels = []
        if self.id is 0:
            for i in self.paths[1]:
                for j in self.paths[2]:
                    for k in self.paths[3]:
                        for m in self.paths[4]:
                            acts = []
                            acts.append(-1)  # represent self id
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
