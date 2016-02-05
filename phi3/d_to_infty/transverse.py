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
        self.projectors = []
        self.get_projectors()


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
                        if [e_from, e_to, e_num] == dot_out:      # dot on in-end
                            if [e_to, e_from, e_num] == dot_in:   # dot on both ends
                                # print "\t\t>>> node %d: dot at" % e_from, dot_out, "and", dot_in
                                print "\t\t>>> P_%d,%d" % (2*e_from+1,2*e_to+1),
                            else:
                                # print "\t\t>>> node %d: dot at" % e_from, dot_out
                                print "\t\t>>> P_%d,%d" % (2*e_from+1,2*e_to),
                        else:
                            if [e_to, e_from, e_num] == dot_in:   # dot on out-end
                                # print "\t\t>>> node %d: dot at" % e_from, dot_in
                                print "\t\t>>> P_%d,%d" % (2*e_from,2*e_to+1),
                            else:
                                # print "\t\t>>> node %d: dot at" % e_from, dot_out # no dots
                                print "\t\t>>> P_%d,%d" % (2*e_from,2*e_to),
                        # print "(%s)" % self.D.edge[e_from][e_to][e_num]['mom']
                        print "(%s)" % self.momenta_in_edge((e_from, e_to, e_num))

    def momenta_in_edge(self,e):
        """
        :param e: (e0,e1,e2) - networkx multigraph edge
        :return: momenta as str, i.e. ['k0+k2+k3'],
            k_N with N = Loops is for the external momentum
        """
        mom = self.U[e[0]][e[1]][e[2]]['mom']
        return "+".join(["k%d"%j for j,k in enumerate(bin(mom)[:1:-1]) if int(k) and j <= self.Loops])

class P():
    """
    Class `Projector`
    """
    def __init__(self,d_graph, edge_tuple):
        e0, e1, e2 = edge_tuple
        self.mom = d_graph.edge[e0][e1][e2]['mom']

if __name__ == "__main__":
    diag1 = "e12|e3|33||:0A_aA_dA|0a_da|aA_dd||"
    d = D(diag1)
    t = transverse(diag1)
    # all the lines:
    print t.U