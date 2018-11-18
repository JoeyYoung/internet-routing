import numpy as np


class T:
    """
        T nodes, clique using peer links
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0
        self.peers_T = []
        self.customers_M = []
        self.customers_CP = []
        self.customers_C = []


class M:
    """
        M nodes, T or M as providers, peer links with M, CP
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0
        self.peer_degree = 0
        self.providers_T = []
        self.providers_M = []
        self.peers_M = []
        self.peers_CP = []
        self.customers_M = []
        self.customers_CP = []
        self.customers_C = []


class CP:
    """
        CP nodes, T or M as providers, peer links with CP or M
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0
        self.providers_T = []
        self.providers_M = []
        self.peers_CP = []
        self.peers_M = []


class C:
    """
        C nodes, T or M as providers, no peer links
    """

    def __init__(self, id):
        self.id = id
        self.degree = 0
        self.providers_T = []
        self.providers_M = []
