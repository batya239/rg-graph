__author__ = 'dima'
import uncertainties
import graphine
from rggraphutil import Ref
values = list()
values.append({0: -0.0037345907622900014, 1: 7.591710077845467e-08})
values.append({0: -0.00205112021826125, 1: 1.7012545e-08})
values.append({0: -0.00205111626901875, 1: 1.7232395e-08})
values.append({0: -0.003734577662621249, 1: 7.434289571084762e-08})
values.append({0: -0.0019831197888575004, 1: 4.0136115353036255e-08})
values.append({0: -0.0009763879736024998, 1: 1.8634342518332415e-08})
values.append({0: -0.0019831071455574992, 1: 8.511509703407404e-08})
values.append({0: -0.0009763869207874999, 1: 1.8954765280613513e-08})
values.append({0: -0.00198311996721625, 1: 3.726468341625622e-08})
values.append({0: -0.0020510983011899995, 1: 5.341229966630374e-08})
values.append({0: -0.001619313505725625, 1: 1.1160189375e-08})
values.append({0: 0.00029843362555875, 1: 1.10981725e-08})
values.append({0: -9.046442397499732e-06, 1: 4.636541679494275e-08})
values.append({0: -9.049835061249872e-06, 1: 4.646302313377157e-08})
values.append({0: 0.000298430232895, 1: 1.149913375e-08})
values.append({0: 0.00029841273829999976, 1: 2.6439894626644814e-08})
values.append({0: -0.0009741324854200002, 1: 2.2077789656788156e-08})
values = map(lambda v: uncertainties.ufloat(v[0], v[1]), values)

graphs = list()
graphs.append("e12_e3_34_5_e6_66__0a_az_za_0a_za_az_za_za_0z_az_za_za__.py")
graphs.append("e12_e3_34_5_e6_66__0a_az_za_0a_za_za_za_za_0z_az_za_za__.py")
graphs.append("e12_e3_34_5_e6_66__0a_za_az_0z_az_az_az_az_0a_za_az_az__.py")
graphs.append("e12_e3_34_5_e6_66__0a_za_az_0z_az_za_az_az_0a_za_az_az__.py")
graphs.append("e12_e3_34_5_e6_66__0a_za_za_0a_za_az_za_za_0z_az_za_za__.py")
graphs.append("e12_e3_34_5_e6_66__0a_za_za_0a_za_za_za_za_0z_az_za_za__.py")
graphs.append("e12_e3_34_5_e6_66__0a_za_za_0z_az_za_az_az_0a_za_az_az__.py")
graphs.append("e12_e3_34_5_e6_66__0z_az_az_0a_az_az_az_az_0a_za_az_az__.py")
graphs.append("e12_e3_34_5_e6_66__0z_az_az_0a_az_za_az_az_0a_za_az_az__.py")
graphs.append("e12_e3_34_5_e6_66__0z_az_az_0a_za_az_az_az_0a_za_az_az__.py")
graphs.append("e12_e3_34_5_e6_66__0z_az_az_0a_za_az_az_za_0a_az_za_za__.py")
graphs.append("e12_e3_45_46_e_66__0a_za_za_0a_za_za_az_za_za_0z_az_az__.py")
graphs.append("e12_e3_45_46_e_66__0a_za_za_0a_za_za_za_za_az_0z_za_za__.py")
graphs.append("e12_e3_45_46_e_66__0z_az_az_0a_az_az_az_az_za_0a_az_az__.py")
graphs.append("e12_e3_45_46_e_66__0z_az_az_0a_az_az_za_az_az_0a_za_za__.py")
graphs.append("e12_e3_45_46_e_66__0z_az_az_0a_za_az_az_az_za_0a_az_az__.py")
graphs.append("e12_e3_45_46_e_66__0z_az_az_0a_za_az_az_za_za_0a_az_az__.py")
graphs = map(lambda g: g.replace("__0", "__:0").replace("_", "|").replace("z", "A")[:-3] + ":::::", graphs)
import graph_util_mr
graphs = map(lambda g: graph_util_mr.from_str_alpha(g), graphs)


IDX=dict()
IDX_V=Ref.create(0)
import graph_state
def graph_idx(g):
    g = graphine.Graph(map(lambda e: e.copy(fields=graph_state.Fields("00")) if e.is_external() else e, g))
    g1 = graphine.Graph(map(lambda e: e.copy(fields=-e.fields), g))
    g2 = g
    if g1 in IDX or g2 in IDX:
        assert IDX[g1] == IDX[g2]
        return IDX[g1]
    IDX_V.set(IDX_V.get() + 1)
    IDX[g1] = IDX_V.get()
    IDX[g2] = IDX_V.get()
    return IDX_V.get()

for g, v in zip(graphs, values):
    print graph_idx(g)
    print v
    # print g
    print "----"