import numpy as np
import operator
import random
from nodes import T
from nodes import M
from nodes import CP
from nodes import C
import collections

'''
    here may be not consider the 'region'
'''


class Generator:
    # init with n number and number of T
    def __init__(self, n, nT):
        self.n = n
        self.nT = nT
        self.nM = int(0.15 * self.n)
        self.nCP = int(0.05 * self.n)
        self.nC = int(0.80 * self.n)
        # other pars for d, p, t
        self.dM = 2 + 2.5 * n / 10000
        self.dCP = 2 + 1.5 * n / 10000
        self.dC = 1 + 5 * n / 100000
        self.pM = 1 + 2 * n / 10000
        self.pCP_M = 0.2 + 2 * n / 10000
        self.pCP_CP = 0.05 + 5 * n / 100000
        self.tM = 0.375
        self.tCP = 0.375
        self.tC = 0.125

        # collections for nodes
        self.Ts = []
        self.Ms = []
        self.CPs = []
        self.Cs = []

        # create object for nodes, init parameters with ids
        # label id from 0 ~ nT-1
        for i in range(self.nT):
            t = T(i)
            self.Ts.append(t)

        # label id from nT ~ nT+nM-1
        for i in range(self.nM):
            m = M(i + self.nT)
            self.Ms.append(m)

        # label id from nT+nM ~ nT+nM+nCP-1
        for i in range(self.nCP):
            cp = CP(i + self.nT + self.nM)
            self.CPs.append(cp)

        # label id from nT+nM+nCP ~ nT+nM+nCP+nC-1
        for i in range(self.nC):
            c = C(i + self.nT + self.nM + self.nCP)
            self.Cs.append(c)

    # create clique for T nodes, complete graph
    # here add peer, need to check if double build
    def add_t_nodes(self):
        for t in self.Ts:
            for t_p in self.Ts:
                if t_p == t: continue
                if t_p in t.peers_T: continue
                t.peers_T.append(t_p)
                t_p.peers_T.append(t)
                t.degree += 1
                t_p.degree += 1

    # add M nodes one by one, with provider determined
    def add_m_nodes(self):
        for m in self.Ms:
            # determine how many provider, uniform distribution between 0-2dM, average dM
            num_providers = random.randint(0, 2 * int(self.dM))

            # preference those with higher degrees, rank with decreasing
            func = operator.attrgetter('degree')
            self.Ts.sort(key=func, reverse=True)
            self.Ms.sort(key=func, reverse=True)

            # number has been determined, sorted, here degree added has no impact
            it = im = 0
            for i in range(num_providers):
                pro = random.random()
                if pro <= self.tM:
                    # provider is T, build relationship
                    pt = self.Ts[it]
                    m.providers_T.append(pt)
                    m.degree += 1
                    pt.customers_M.append(m)
                    pt.degree += 1
                    it += 1

                else:
                    # provider is M, build relationship
                    pm = self.Ms[im]
                    # avoid itself as provider
                    if pm == m:
                        im += 1
                        pm = self.Ms[im]
                    m.providers_M.append(pm)
                    m.degree += 1
                    pm.customers_M.append(m)
                    pm.degree += 1
                    im += 1

    # same as M nodes
    def add_cp_nodes(self):
        for cp in self.CPs:
            num_providers = random.randint(0, 2 * int(self.dCP))
            func = operator.attrgetter('degree')
            self.Ts.sort(key=func, reverse=True)
            self.Ms.sort(key=func, reverse=True)

            it = im = 0
            for i in range(num_providers):
                pro = random.random()
                if pro <= self.tCP:
                    # provider is T, build relationship
                    pt = self.Ts[it]
                    cp.providers_T.append(pt)
                    cp.degree += 1
                    pt.customers_CP.append(cp)
                    pt.degree += 1
                    it += 1

                else:
                    # provider is M, build relationship
                    pm = self.Ms[im]
                    cp.providers_M.append(pm)
                    cp.degree += 1
                    pm.customers_CP.append(cp)
                    pm.degree += 1
                    im += 1

    # same as M nodes
    def add_c_nodes(self):
        for c in self.Cs:
            num_providers = random.randint(0, 2 * int(self.dC))
            func = operator.attrgetter('degree')
            self.Ts.sort(key=func, reverse=True)
            self.Ms.sort(key=func, reverse=True)

            it = im = 0
            for i in range(num_providers):
                pro = random.random()
                if pro <= self.tC:
                    # provider is T, build relationship
                    pt = self.Ts[it]
                    c.providers_T.append(pt)
                    c.degree += 1
                    pt.customers_C.append(c)
                    pt.degree += 1
                    it += 1

                else:
                    # provider is M, build relationship
                    pm = self.Ms[im]
                    c.providers_M.append(pm)
                    c.degree += 1
                    pm.customers_C.append(c)
                    pm.degree += 1
                    im += 1

    # add peering links, PEER_DEGREE & DEGREE
    def add_m_peers(self):
        for m in self.Ms:
            # determine the number of peer links for each M, half it
            # only consider one-direct out peer, but add degree both
            number_peers = random.randint(0, int(1 * self.pM))
            # sort based on peer degree
            func = operator.attrgetter('peer_degree')
            self.Ms.sort(key=func, reverse=True)
            # build relationship
            im = 0
            for i in range(number_peers):
                pm = self.Ms[im]
                # avoid self
                if pm == m:
                    im += 1
                    pm = self.Ms[im]
                # avoid relationship that have been already built
                while pm in m.providers_M or pm in m.customers_M:
                    im += 1
                    pm = self.Ms[im]
                m.peers_M.append(pm)
                m.peer_degree += 1
                m.degree += 1
                pm.peers_M.append(m)
                pm.peer_degree += 1
                pm.degree += 1
                im += 1

    # equally choose every peers
    def add_cp_peers(self):
        for cp in self.CPs:
            number_peers_m = random.randint(0, int(1 * self.pCP_M))
            number_peers_cp = random.randint(0, int(1 * self.pCP_CP))

            # build relationship
            for i in range(number_peers_m):
                pm = random.choice(self.Ms)
                while pm in cp.providers_M:
                    pm = random.choice(self.Ms)
                cp.peers_M.append(pm)
                pm.peers_CP.append(cp)
                pm.peer_degree += 1
                cp.degree += 1
                pm.degree += 1
            for i in range(number_peers_cp):
                cpp = random.choice(self.CPs)
                while cpp == cp:
                    cpp = random.choice(self.CPs)
                cp.peers_CP.append(cpp)
                cpp.peers_CP.append(cp)
                cp.degree += 1
                cpp.degree += 1

    """
        considering BGP advertisement to providers
    """
    def advertise_c_to_provider(self):
        # c has no peers, no customers
        # TODO, from low to high. advertise learned from customer to provider(T, M), M recursion

    def advertise_cp_to_provider(self):
        # co has peers, no customers
        # TODO, from low to high. advertise learned from customer to provider(T, M), M recursion

    def advertise_m_to_provider(self):
        # TODO, used for recursion. advertise learned from customer to provider(T, M), M recursion

    """
        considering BGP advertisement to peers
    """
    def advertise_t_to_peers(self):
        # TODO, advertise learned from customer to peers

    def advertise_m_to_peers(self):
        # TODO, advertise learned from customer to peers

    def advertise_cp_to_peers(self):
        # TODO, advertise learned from customer to peers

    """
        considering BGP advertisement to customer
    """
    def advertise_t_to_customers(self):
        # TODO, advertise all table(peers, pc) to customers

    def advertise_m_to_customers(self):
        # TODO, advertise all table(peers, pc) to customers


'''
    TEST CASE
'''
generator = Generator(10000, 6)
generator.add_t_nodes()
generator.add_m_nodes()
generator.add_c_nodes()
generator.add_cp_nodes()
generator.add_m_peers()
generator.add_cp_peers()
for m in generator.Cs:
    print(m.degree)

# node = generator.CPs[4]
# print(node.id)
# if len(node.providers_M) > 0:
#     print(node in node.providers_M[0].customers_CP)
# if len(node.providers_T) > 0:
#     print(node in node.providers_T[0].customers_CP)
