#!/usr/bin/python
# -*- coding: utf8
from TaskScheduler.task_scheduler import task, log

__author__ = 'dima'


import time
import os


class MasterNode(object):
    KILL_FILE = ".kill"
    STARTED_FILE = ".started"

    def __init__(self, directory, watch_interval=10):
        if not os.path.exists(directory):
            os.mkdir(directory)
        started_file = os.path.join(directory, MasterNode.STARTED_FILE)
        if os.path.exists(started_file):
            raise ValueError("Can't start yet another one scheduler in same folder '%s'" % directory)
        open(started_file, 'a').close()
        self._directory = directory
        self._watch_interval = watch_interval

    @property
    def directory(self):
        return self._directory

    def run(self):
        log.info("scheduler started in '%s'" % self.directory)
        while True:
            log.debug("heartbeat")
            if self.watch_for_exit():
                return
            self.watch_for_new_tasks()
            time.sleep(self._watch_interval)

    def watch_for_new_tasks(self):
        tasks_to_run = list()

        for f in os.listdir(self._directory):
                task_directory = os.path.join(self._directory, f)
                if os.path.isdir(task_directory):
                    t = task.Task(task_directory, task.TaskSettings.parse_from_file(task_directory, self), self)
                    status = t.get_status()
                    if task.STATUS_NEW == status and t.mark_status():
                        log.info("new task '%s' found" % f)
                        tasks_to_run.append(t)

        def run_task(t):
            t.set_status(task.STATUS_RUN)
            log.info("run task '%s'" % os.path.basename(t.task_dir))
        map(lambda t: run_task(t), tasks_to_run)
        task.run_tasks(tasks_to_run)

    def watch_for_exit(self):
        kill_file_path = os.path.join(self._directory, MasterNode.KILL_FILE)
        if os.path.exists(kill_file_path):
            os.remove(kill_file_path)
            os.remove(os.path.join(self._directory, MasterNode.STARTED_FILE))
            log.info("scheduler exit")
            return True
        else:
            return False