#! encoding: utf8
from d_to_infty_class import D_to_infty_graph as D

__author__ = 'kirienko'


# Here we check whether transverseness matters

class transverse(D):
    """
    Projector is:
        P_i,j (k) = δᵢⱼ-kᵢkⱼ/k²
    """

    def __init__(self, nickel_str):
        # call parental constructor first
        D.__init__(self, nickel_str)

    def flow_near_node_0(self, node):
        """
        Returns the number of simple momenta that flows through the node
        by the dotted edge (binary string like '0100').
        For directed graphs only.
        """
        mom = []
        pr = self.D.predecessors(node)
        for n in pr:
            for nn in self.D[n][node]:
                if 'd' == self.D[n][node][nn]['fields'][-1]:
                    continue
                mom += [self.D[n][node][nn]['mom']]
        to_nodes = self.D.successors(node)
        for n in to_nodes:
            for nn in self.D[node][n]:
                if 'd' == self.D[node][n][nn]['fields'][0]:
                    continue
                mom += [self.D[node][n][nn]['mom']]

        return mom[0] & mom[1]

    def flow_near_node_phi(self, node, field_type='phi'):
        """
        Returns the number of simple momenta that flows through the node
        (only either φ-edge or φ'-edge is taken into account)
        by the dotted edge (binary string like '0100').
        For directed graphs only.
        """
        if field_type == 'phi':
            field = 'a'
        elif field_type == 'phiprime':
            field = 'A'
        else:
            raise
        pr = self.D.predecessors(node)
        for n in pr:
            for nn in self.D[n][node]:
                if field == self.D[n][node][nn]['fields'][-1]:
                    return self.D[n][node][nn]['mom']
        to_nodes = self.D.successors(node)
        for n in to_nodes:
            for nn in self.D[node][n]:
                if field == self.D[node][n][nn]['fields'][0]:
                    return self.D[node][n][nn]['mom']

    def get_projectors(self):
        """
        Lets suppose that you were able every night to dream any dream you wanted to dream,
        and you would naturally as you began on this adventure of dreams,
            you would fulfill all your wishes.
        You would have every kind of pleasure, you see,
            and after several nights you would say,
            well that was pretty great, but now lets have a surprise,
            lets have a dream which isn't under control.
        Well something is going to happen to me that i don't know what it's gonna be.
        Then you would get more and more adventurous, and you would make
            further and further out gambles as to what you would dream,
            and finally you would dream where you are now.
            If you awaken from this illusion and you understand
                black implies white,
                self implies other,
                life implies death.
            You can feel yourself not as a stranger in the world
                not as something here on vacation
                not as something that has arrived..
                what you are basically far far in
                    is simply the fabric and structure of existence itself...
        :return:
        """
        for e_from in self.D.edge.keys():
            if e_from >= 0:
                dot_out = [e_from] + list(self.D.node[e_from]['dot'])
                for e_to in self.D.edge[e_from].keys():
                    # print "\t", (e_from,e_to), self.D.edge[e_from][e_to]
                    for e_num in self.D.edge[e_from][e_to].keys():
                        dot_in = [e_to] + list(self.D.node[e_to]['dot'])
                        if [e_from, e_to, e_num] == dot_out:  # dot on in-end
                            if [e_to, e_from, e_num] == dot_in:  # dot on both ends
                                # print "\t\t>>> node %d: dot at" % e_from, dot_out, "and", dot_in
                                print "\t\t>>> P_%d,%d" % (2 * e_from + 1, 2 * e_to + 1),
                            else:
                                # print "\t\t>>> node %d: dot at" % e_from, dot_out
                                print "\t\t>>> P_%d,%d" % (2 * e_from + 1, 2 * e_to),
                        else:
                            if [e_to, e_from, e_num] == dot_in:  # dot on out-end
                                # print "\t\t>>> node %d: dot at" % e_from, dot_in
                                print "\t\t>>> P_%d,%d" % (2 * e_from, 2 * e_to + 1),
                            else:
                                # print "\t\t>>> node %d: dot at" % e_from, dot_out # no dots
                                print "\t\t>>> P_%d,%d" % (2 * e_from, 2 * e_to),
                        # print "(%s)" % self.D.edge[e_from][e_to][e_num]['mom']
                        print "(%s)" % self.momenta_in_edge((e_from, e_to, e_num))

    def momenta_in_edge(self, e):
        """
        :param e: (e0,e1,e2) - networkx multigraph edge
        :return: momenta as str, i.e. ['k0+k2+k3'],
            k_N with N = Loops is for the external momentum
        """
        mom = self.U[e[0]][e[1]][e[2]]['mom']
        return "+".join(["k%d" % j for j, k in enumerate(bin(mom)[:1:-1]) if int(k) and j <= self.Loops])

    def test(self):
        bridges = {}
        for (b1, b2) in self.bridges:
            # print "Bridge %d-%d" % (b1,b2)
            mom_0_1, mom_0_2 = int(self.flow_near_node_0(b1)), int(self.flow_near_node_0(b2))
            # print "\t0:", mom_0_1, mom_0_2, "==>", mom_0_1 & mom_0_2
            mom_7_1, mom_7_2 = self.flow_near_node_phi(b1, 'phi'), self.flow_near_node_phi(b2, 'phi')
            # print "\t7:", mom_7_1, mom_7_2, "==>", mom_7_1  & mom_7_2
            # print "\t8:", mom_8_1, mom_8_2, "==>", mom_8_1  & mom_8_2
            bridges[(b1, b2)] = [mom_0_1 & mom_0_2, mom_7_1 & mom_7_2]

        for k, b in bridges.items():
            if not all(x == b[0] for x in b):
                return False
        return True


if __name__ == "__main__":
    diag1 = "e12|e3|33||:0A_aA_dA|0a_da|aA_dd||"
    diag2 = "e12|34|34|5|5|e|:0A_aA_dA|aA_dd|dd_aa|aA|Ad|0a|"
    with open('4loop_nonzero.txt') as fd:
        data = fd.readlines()
    diags = [d.strip() for d in data]

    from minimal_diag_set_l3e1 import final

    # for j,diag in enumerate(final):
    # for j,diag in enumerate(diags):
    #     d = transverse(diag.replace('-','|'))
    #     print j, diag,
    #     print d.test()

    good = [d for d in diags if transverse(d).test()]
    # good = [d.replace('|','-') for d in final if transverse(d.replace('-','|')).test()]
    print len(good)  # , good

    # print final
    # print len([f for f in final if f.replace('-','|') in good])
    # for f in final:
    #     print f, f in good
