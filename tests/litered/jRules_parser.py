#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sys
import re

_SECTOR_REGEXP = re.compile("^\[(.*)\] /; (.*) -> (.*)$")
_SECTOR_CONDITION_REGEXP = re.compile(".*n(.+)_\)\?(.+)")


def convert_rule(rule_string):
    result = re.sub("j\[([^,]+),([^\]]+)\]", "j_\\1(\\2)", rule_string)
    result = re.sub("\s+", " ", result)
    return result


def convert_sector_conditions(sector_condition_string):
    result = dict()
    vars_string = sector_condition_string.split(',')[1:]
    for item in vars_string:
        regex_result = _SECTOR_CONDITION_REGEXP.match(item)
        if regex_result:
            n, value = regex_result.groups()
            value = value.rstrip()
            if value == 'Positive':
                result[int(n)] = 1
            elif value == 'NonPositive':
                result[int(n)] = 0
            else:
                raise NotImplementedError(value)

    return result


def parse_additional_conditions(conditions_string):
    result = conditions_string.replace("||", "or").replace("&&", "and").replace("!(", "not (")
    result = re.sub("\s+", " ", result)
    return result


def parse_rule(rule_string, n):
    regex_result = _SECTOR_REGEXP.match(rule_string)
    if regex_result:
    #       print regex_result.groups()
        print convert_sector_conditions(regex_result.groups()[0])
        print parse_additional_conditions(regex_result.groups()[1])
        print convert_rule(regex_result.groups()[2])

    return None


jrules_string = ''.join(map(lambda x: x.rstrip(), open(sys.argv[1]).readlines()))[2:-1].split(', j')
for item in jrules_string:
#    print item
    parse_rule(item, 5)
#    break
#print jrules_string

