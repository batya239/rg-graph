#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import kr1
import cuba_integration
import os
import subprocess
from task_scheduler import submit_job, check_job_status, STATUS_DONE, STATUS_NEW, STATUS_RUN, STATUS_FAILED
from rggraphutil import zeroDict
from uncertainties import ufloat
import configure_mr
import atexit
import traceback
import sys

OPERATION_NAMES = dict()
OPERATION_NAMES[""] = kr1.kr1_log_divergence
OPERATION_NAMES["w"] = kr1.kr1_d_iw
OPERATION_NAMES["p"] = kr1.kr1_d_p2

OUTPUT_FILE_NAME = "output.txt"


AGGREGATION_FILE_TEMPLATE = """#!/usr/bin/env python
# -*- coding: utf8

from momentumrepr import aggregation

SCHEDULER_DIR = \"{scheduler_dir}\"
TASK_NAMES = {task_names}

aggregation(SCHEDULER_DIR, TASK_NAMES)
"""


JOB_EXECUTABLE = """#!/usr/bin/env python
# -*- coding: utf8


from momentumrepr import cuba_execute, configure_mr
import os

configure_mr.Configure().\
    with_integration_algorithm("{algorithm}").\
    with_maximum_points_number("{max_points}").\
    with_absolute_error({abs_err}).\
    with_relative_error({rel_err}).configure()

d = cuba_execute(os.path.abspath("./"))

print dict(map(lambda (k, v): (k, (v.n, v.s)), d.iteritems()))
"""


@atexit.register
def on_shutdown():
    if configure_mr.Configure.delete_integration_tmp_dir_on_shutdown():
        subprocess.call(["rm", "-rf", "tmp/"])


def calculate_diagram(graph_state_str, operation_name, task_server_dir, aggregator_dir):
    if operation_name not in OPERATION_NAMES.keys():
        raise ValueError("operation_name argument must be on of %s" % OPERATION_NAMES.keys())
    aggregator_dir = os.path.expanduser(aggregator_dir)
    aggregator_dir = os.path.abspath(aggregator_dir)
    if not os.path.exists(aggregator_dir):
        os.mkdir(aggregator_dir)

    task_names = list()

    with open("job_executable.py", "w") as f:
        args = {'algorithm': configure_mr.Configure.integration_algorithm(),
                  'max_points': configure_mr.Configure.maximum_points_number(),
                  'abs_err': configure_mr.Configure.absolute_error(),
                  'rel_err': configure_mr.Configure.relative_error()}
        f.write(JOB_EXECUTABLE.format(**args))

    for integrand in OPERATION_NAMES[operation_name](graph_state_str):
        integrator_dir = cuba_integration.cuba_generate(*integrand)
        task_name = os.path.basename(integrator_dir)
        task_names.append(task_name)
        task_files = [os.path.abspath("./job_executable.py")]
        task_executable_name = "job_executable.py"

        for f in os.listdir(integrator_dir):
            task_files.append(os.path.join(integrator_dir, f))
        submit_job(task_server_dir, task_name, task_files, task_executable_name, OUTPUT_FILE_NAME)
        print "job '%s' submitted" % task_name

    aggregation_file_name = graph_state_str.replace("|", "-").replace(":", "#") + operation_name + ".py"
    aggregation_file_name = os.path.join(aggregator_dir, aggregation_file_name)
    aggregation_file_name = os.path.expanduser(aggregation_file_name)
    aggregation_file_name = os.path.abspath(aggregation_file_name)

    with open(aggregation_file_name, 'w') as f:
        f.write(AGGREGATION_FILE_TEMPLATE.format(**{"scheduler_dir": task_server_dir, "task_names": task_names}))

    print "all jobs submitted, aggregation file generated"


def aggregation(scheduler_path, task_names):
    scheduler_path = os.path.expanduser(scheduler_path)
    scheduler_path = os.path.abspath(scheduler_path)
    answer = zeroDict()
    done_tasks = 0
    for task_name in task_names:
        status = check_job_status(scheduler_path, task_name)
        if status == STATUS_FAILED:
            print "job '%s' failed" % task_name
            return
        elif status == STATUS_RUN or status == STATUS_NEW:
            print "job '%s' in progress (%s)" % (task_name, status)
        elif status == STATUS_DONE:
            try:
                with open(os.path.join(scheduler_path, task_name, OUTPUT_FILE_NAME), "r") as f:
                    content = f.read()
                    try:
                        d = eval(content.split("\n")[-2])
                        done_tasks += 1
                        for k, v in d.iteritems():
                            answer[k] += ufloat(v[0], v[1])
                    except Exception as e:
                        print "\n" + "".join(traceback.format_tb(sys.exc_info()[2]))
                        print e
                        print "something wrong with job '%s', content = %s" % (task_name, content)
            except Exception as e:
                print "\n" + "".join(traceback.format_tb(sys.exc_info()[2]))
                print e
                print "something wrong with job '%s'" % task_name
                return
    print "%s/%s done" % (done_tasks,len(task_names))
    print "result =", answer
