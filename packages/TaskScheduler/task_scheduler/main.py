#!/usr/bin/python
# -*- coding: utf8
from TaskScheduler.task_scheduler import utils

__author__ = 'dima'


def main():
    utils.start_scheduler("~/.server", 1)

if __name__ == "__main__":
    main()