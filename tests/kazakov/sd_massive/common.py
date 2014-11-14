#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'
import os
import imp


def load_config(config_file=None):
    """
    function loads config file for scons, return values is module with settings that can be used in scons files
    priority for loading configs is the following:
    1. if config_file is not None load settings from this file
    2. ./scons_config.py from current dir
    3. scons_config.py from  ~/.rg-graph/
    4. scons_config.py from scons template dir
    """
    config_priority = [] if config_file is None else [config_file]
    config_priority += ['./scons_config.py', os.path.join(os.environ['PATH'], '.rg-graph/scons_config.py')]
    config = None
    for filename in config_priority:
        try:
            config = imp.load_source("scons_config", filename)
            print "Using config %s" % filename
            break
        except IOError:
            pass
    if config is None:
        import scons_config as config

        print "Using default config"
    return config

