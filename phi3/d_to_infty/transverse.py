from d_to_infty_class import D_to_infty_graph as D

# Here we check whether transversness matters

class transverse(D):
    def projectors(self):
        pass

if __name__ == "__main__":
    diag1 = "e12|e3|33||:0A_aA_dA|0a_da|aA_dd||"
    d = D(diag1)
    t = transverse(diag1)
    # all the lines:
    print t.U