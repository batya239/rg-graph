#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from task_scheduler import submit_job, check_job_status, STATUS_DONE, STATUS_FAILED, STATUS_NEW, STATUS_RUN
from rggraphenv import symbolic_functions
try:
    import configure_mr
except:
    from momentumrepr import configure_mr

configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.CLN_TWO * symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(50000000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-8).\
    with_integration_algorithm("vegas").\
    with_debug(True).configure()

operation = "iw"

TASK_TEMPLATE = """#!/usr/bin/env python
# -*- coding: utf8

from rggraphenv import symbolic_functions
from rggraphutil import zeroDict
from momentumrepr import configure_mr
from momentumrepr.ms import t_2_groups
from momentumrepr.ms import t_3_groups
from momentumrepr.ms import kr1
from momentumrepr.ms import integration
from momentumrepr.ms import graph_util_ms

configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.CLN_TWO * symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number({maxpoints}).\
    with_absolute_error({abse}).\
    with_relative_error({rele}).\
    with_integration_algorithm({algorithm}).\
    with_debug(True).configure()

graphs = {graph_source}
op = kr1.compound_kr1 if isinstance(graphs, list) else kr1.kr1

def multiply(dict_a, dict_b):
    dict_c = zeroDict()
    for k, v in dict_a.iteritems():
        for k2, v2 in dict_b.iteritems():
            dict_c[k + k2] += v * v2
    return dict_c

r = symbolic_functions.CLN_ZERO
r1 = zeroDict()
for t in op(graphs):
    p2_dotes = 0
    if len(t) == 3:
        assert isinstance(graphs, list)
        p2_dotes = t[2]
    k = t[0]
    v = t[1]
    diag_res = integration.calculate(k, \"{operation}\", p2_dotes)
    r += integration.apply_tau(diag_res, k) * v.eval_with_tau()
    multiplier_res = v.eval_with_error()
    for k, v in multiply(diag_res, multiplier_res).items():
        r1[k] += v
with open("result.log", "w") as f:
    f.write('{graph_source}' + "\\n")
    f.write(str(symbolic_functions.pole_part(r, remove_order=False).evalf()) + "\\n")
    f.write(str(integration.K(r1)) + "\\n")
print "RESULT TAU", symbolic_functions.pole_part(r, remove_order=False).evalf()
print "RESULT DICT", integration.K(r1)
"""

AGGREGATION_TEMPLATE = """#!/usr/bin/python
# -*- coding: utf8

import os
from task_scheduler import submit_job, check_job_status, STATUS_DONE, STATUS_FAILED, STATUS_NEW, STATUS_RUN

def aggregate(job_name):
    status = check_job_status("~/.server", job_name)
    print status
    if status == STATUS_DONE:
        with open(os.path.expanduser(os.path.join("~/.server", job_name, "result.log"))) as f:
            for l in f:
                print l

aggregate(\"{job_name}\")
"""




if __name__ == "__main__":
    import t_2_groups
    import t_3_groups
    import os

    graphs = (t_3_groups if operation == "log" else t_2_groups).get_all_sources()

    pure_graphs = graphs[0]
    compound_graphs = graphs[1]

    all_graphs = map(lambda g: "graph_util_ms.from_str(\"%s\")" % g, pure_graphs) + \
                 map(lambda f: ("t_3_groups" if operation == "log" else "t_2_groups") + "." + f + "()", compound_graphs)

    for g in all_graphs:
        job_name = g.replace("\"", "").replace("|", "-").replace(":", "#").replace("A", 'z').replace("(", "").replace(")", "") + operation
        with open("job_executable", "w") as f:
            f.write(TASK_TEMPLATE.format(**{'maxpoints': configure_mr.Configure.maximum_points_number(),
                             'abse': configure_mr.Configure.absolute_error(),
                             'rele': configure_mr.Configure.relative_error(),
                             'algorithm': configure_mr.Configure.integration_algorithm(),
                             'graph_source': g,
                             'operation': operation}))
        submit_job("~/.server", job_name, [os.path.join(os.getcwd(), "job_executable")], ["job_executable"], job_output_file="job.log")
        os.remove("job_executable")

        with open(os.path.join(os.path.expanduser("~/.aggregator"), job_name + ".py"), 'w+') as f:
            f.write(AGGREGATION_TEMPLATE.format(**{'job_name': job_name}))


