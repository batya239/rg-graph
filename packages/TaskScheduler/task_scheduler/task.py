#!/usr/bin/python
# -*- coding: utf8
from TaskScheduler.task_scheduler import log

__author__ = 'dima'


import os
import subprocess
import sys
import traceback
import stat
from IPython.parallel import Client

FAIL_MESSAGE_FILE_NAME = ".fail-message"
TASK_SETTINGS_FILE_NAME = ".settings"

STATUS_NEW = ".new"
STATUS_RUN = ".run"
STATUS_DONE = ".done"
STATUS_FAILED = ".failed"

STATUSES = {STATUS_NEW, STATUS_DONE, STATUS_RUN, STATUS_FAILED}
FINISHED_STATUSES = {STATUS_FAILED, STATUS_DONE}

PROFILE = "mpi"


def async_map(function, iterable):
    the_map = None
    if the_map is None:
        try:
            c = Client(profile=PROFILE)
            dview = c[:]
            the_map = dview.map_async
            log.debug("concurrency using IPython enabled")
            with dview.sync_imports():
            if dview is None or len(dview) == 0:
                raise ValueError("dview is empty")
        except BaseException as e:
            the_map = map
            log.debug("concurrency no enabled")

    return the_map(function, iterable)


def run(t):
    executable_abs_path = os.path.join(t.task_dir, t.task_settings.executable_name)
    redirect_output = None if t.task_settings.redirect_output is None else os.path.join(t.task_dir, t.task_settings.redirect_output)
    log.info("starting new task '%s'" % os.path.basename(t.task_dir))
    try:
        output = open(redirect_output, 'w')
        os.chmod(executable_abs_path, os.stat(executable_abs_path).st_mode | stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
        return_code = subprocess.Popen(executable_abs_path, stdout=output, cwd=os.path.dirname(executable_abs_path)).wait()
        if return_code != 0:
            log.error("task '%s' return code == %s" % (os.path.basename(t.task_dir), return_code))
            t.set_status(STATUS_FAILED)
            t.set_fail_message("process return code: %s" % return_code)
        else:
            log.info("task '%s' finished successful" % os.path.basename(t.task_dir))
            t.set_status(STATUS_DONE)
    except BaseException as e:
        log.error(executable_abs_path)
        log.error("\n" + "".join(traceback.format_tb(sys.exc_info()[2])))
        log.error("exception while task '%s' executing - '%s'" % (os.path.basename(t.task_dir), e))
        t.set_status(STATUS_FAILED)
        t.set_fail_message(str(e))


def run_tasks(tasks):
    if not len(tasks):
        return
    async_map(run, tasks)


class Task(object):
    def __init__(self, task_dir, task_settings, master):
        self._task_dir = task_dir
        self._task_settings = task_settings
        self._master = master

    @property
    def task_dir(self):
        return self._task_dir

    @property
    def task_settings(self):
        return self._task_settings

    def get_status(self):
        for status in STATUSES:
            status_file_path = os.path.join(self.task_dir, status)
            if os.path.exists(status_file_path):
                return status
        else:
            return None

    def set_status(self, status):
        if status not in STATUSES:
            raise ValueError("invalid task status: %s" % status)
        for s in STATUSES:
            status_file = os.path.join(self.task_dir, s)
            if os.path.exists(status_file):
                os.remove(status_file)
        open(os.path.join(self.task_dir, status), 'a').close()
        return status

    def mark_status(self):
        status = self.get_status()
        status_file_path = os.path.join(self.task_dir, status)
        with open(status_file_path, 'r+') as f:
            content = f.read()
            if content == "CHECKED":
                return False
            else:
                f.write("CHECKED")
                return True

    def set_fail_message(self, message):
        status_file_path = os.path.join(self._master.directory, self.task_dir, FAIL_MESSAGE_FILE_NAME)
        with open(status_file_path, 'w') as f:
            f.write(message)


class TaskSettings(object):
    def __init__(self, redirect_output=None, executable_name=None):
        self._redirect_output = redirect_output
        self._executable_name = executable_name

    @property
    def executable_name(self):
        return self._executable_name

    @property
    def redirect_output(self):
        return self._redirect_output

    def as_dict(self):
        return dict(map(lambda (k, v): (k[1:], v), self.__dict__.iteritems()))

    @staticmethod
    def parse_from_file(task_dir, master_node):
        settings_file_path = os.path.join(master_node.directory, task_dir, TASK_SETTINGS_FILE_NAME)
        with open(settings_file_path, 'r') as content_file:
            content = content_file.read()
        if content is None:
            return None
        kwargs = eval(content)
        return TaskSettings(**kwargs)

    def write_to_file(self, task_dir):
        settings_file_path = os.path.join(task_dir, TASK_SETTINGS_FILE_NAME)
        with open(settings_file_path, 'w') as content_file:
            content_file.write(str(self.as_dict()))