__author__ = 'dima'

f = open("/Users/dima/1.log", "r")

g = None
ids = list()
for l in f:
    if "Time Version:" in l:
        l = l[14:-14]
        if g != l:
            if g != None:
                graph_state_str = g
                operation_name = ""
                import os
                aggregator_dir = "/Users/dima/.aggregator"
                aggregation_file_name = graph_state_str.replace("|", "_").replace(":", "").replace("A",
                                                                                                   "z") + operation_name + ".py"
                aggregation_file_name = os.path.join(aggregator_dir, aggregation_file_name)
                aggregation_file_name = os.path.expanduser(aggregation_file_name)
                aggregation_file_name = os.path.abspath(aggregation_file_name)

                import cluster_runner
                with open(aggregation_file_name, 'w') as f:
                    f.write(cluster_runner.AGGREGATION_FILE_TEMPLATE.format(**{"scheduler_dir": "~/.server", "task_names": ids}))

                print g
                print ids
            ids = list()
            g = l
    if "submitted" in l and '14' in l:
        ids.append(l[l.index('\'') + 1:l.rindex('\'')])
