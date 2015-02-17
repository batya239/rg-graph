#!/usr/bin/python
# -*- coding: utf8
import master_node, task

__author__ = 'dima'


import os
import shutil
import task
import stat
import log
import master_node


def start_scheduler(server_directory, watch_interval=10):
    server_directory = os.path.expanduser(server_directory)
    server_directory = shutil.abspath(server_directory)
    master_node.MasterNode(server_directory, watch_interval).run()


def stop_scheduler(server_directory):
    server_directory = os.path.expanduser(server_directory)
    server_directory = shutil.abspath(server_directory)
    if not os.path.exists(server_directory):
        print "Directory '%s' not exists." % server_directory
        return
    if not os.path.isdir(server_directory):
        print "'%s' is not directory." % server_directory
        return
    open(os.path.join(server_directory, master_node.MasterNode.KILL_FILE), 'a+').close()
    print "Please wait for server stop, run tasks will be finished."


def submit_job(server_directory, job_name, job_files_absolute_paths, job_executable_name, job_output_file=None):
    server_directory = os.path.expanduser(server_directory)
    server_directory = shutil.abspath(server_directory)

    job_dir = os.path.join(server_directory, job_name)
    if os.path.exists(job_dir):
        shutil.rmtree(job_dir)
    os.mkdir(job_dir)
    task.TaskSettings(executable_name=job_executable_name, redirect_output=job_output_file).write_to_file(job_dir)
    for file_path in job_files_absolute_paths:
        file_path = os.path.expanduser(file_path)
        file_path = shutil.abspath(file_path)
        copied_path = os.path.join(job_dir, os.path.basename(file_path))
        shutil.copyfile(file_path, copied_path)
        if job_executable_name == os.path.basename(file_path):
            os.chmod(copied_path, os.stat(copied_path).st_mode | stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
    open(os.path.join(job_dir, task.STATUS_NEW), 'a+').close()


def check_job_status(server_directory, job_name):
    server_directory = os.path.expanduser(server_directory)
    server_directory = shutil.abspath(server_directory)

    for status in task.STATUSES:
        if os.path.exists(os.path.join(server_directory, job_name, status)):
            return status