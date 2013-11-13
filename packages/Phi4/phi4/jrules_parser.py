#!/usr/bin/python
# -*- coding: utf8
__author__ = ['mkompan', 'dima']

import sys
import re
import sector

_SECTOR_REGEXP = re.compile("^\[(.*)\] /; (.*) -> (.*)$")
_SECTOR_CONDITION_REGEXP = re.compile(".*n(.+)_\)\?(.+)")
_EXPAND_REGEXP = re.compile(".*Expand\[(.*)$")
_JS_REGEXP = re.compile("(js[^\]]+\])")
_SECTOR_SECTOR_REGEXP = re.compile("(Sector[^\)]+\))")
_DEBUG = False


def _read_raw_zero_sectors(zero_sectors_string, j_suffix):
    _zero_sectors_string = zero_sectors_string[1: -2]
    return set(map(lambda s: s.replace("js[%s, " % j_suffix, "Sector(").replace("]", ")"), _JS_REGEXP.findall(_zero_sectors_string)))


def _create_zero_rules(raw_zero_sectors):
    result = list()
    for rs in raw_zero_sectors:
        propagators = list()
        for e in eval(rs[6:]):
            if e == 1:
                propagators.append(sector.SectorRule.PROPAGATOR_CONDITION_POSITIVE)
            else:
                propagators.append(sector.SectorRule.PROPAGATOR_CONDITION_NOT_POSITIVE)
        result.append(sector.SectorRule.create_zero_rule(propagators))
    return result


def _convert_rule(rule_string, j_suffix):
    result = re.sub("j\[([^,]+),([^\]]+)\]", "j_\\1(\\2)", rule_string)
    result = re.sub("\s+", " ", result)
    result = result.replace("j_%s" % j_suffix, "Sector")
    return _replace_n(result)


def _replace_zeros(rule_string, raw_zero_sectors):
    result = rule_string
    to_replace = list()
    for m in _SECTOR_SECTOR_REGEXP.finditer(rule_string):
        if m.group() in raw_zero_sectors or "-1" in m.group():
            to_replace.append(m.regs[0])
    while len(to_replace):
        p = to_replace.pop()
        result = result[:p[0]] + "0" + result[p[1]:]
    return result


def _parse_strange_rule(rule_string, j_suffix, raw_zero_sectors):
    _rule_string = _EXPAND_REGEXP.match(rule_string)
    _rule_string = _rule_string.groups()
    if not _rule_string or not len(_rule_string):
        raise ValueError(_rule_string)
    _rule_string = _rule_string[0]
    _rule_string = re.sub("j\[([^,]+),([^\]]+)\]", "j_\\1(\\2)", _rule_string)
    _rule_string = _rule_string.replace("j_%s" % j_suffix, "Sector")
    _rule_string = re.sub("\s+", " ", _rule_string)
    _rule_string = re.sub("\(\s", "(", _rule_string)
    _rule_string = _replace_zeros(_rule_string, raw_zero_sectors)
    _rule_string = _replace_n(_rule_string)
    _rule_string = _rule_string.split("/")
    assert len(_rule_string) in (1, 2)
    if _DEBUG:
        print "STRANGE STRING", _rule_string
    return _rule_string[0], _rule_string[1] if len(rule_string) == 2 else None


def _convert_sector_conditions(sector_condition_string):
    result = list()
    vars_string = sector_condition_string.split(',')[1:]
    for item in vars_string:
        regex_result = _SECTOR_CONDITION_REGEXP.match(item)
        if regex_result:
            n, value = regex_result.groups()
            value = value.rstrip()
            if value == 'Positive':
                result.append(sector.SectorRule.PROPAGATOR_CONDITION_POSITIVE)
            elif value == 'NonPositive':
                result.append(sector.SectorRule.PROPAGATOR_CONDITION_NOT_POSITIVE)
            else:
                raise AssertionError("%s is incorrect sector condition" % value)
    return result


def _parse_additional_condition(condition_string):
    raw_result = condition_string.replace("||", "or").replace("&&", "and").replace("!(", "not (")
    raw_result = re.sub("\s+", " ", raw_result)
    return _replace_n(raw_result)


def _replace_n(string):
    return re.sub('n(\d+)', '{\\1}', string)


def _parse_rule(rule_string, j_suffix, raw_zero_sectors):
    regex_result = _SECTOR_REGEXP.match(rule_string)
    if regex_result:
        return sector.SectorRule(_convert_sector_conditions(regex_result.groups()[0]),
                                 _parse_additional_condition(regex_result.groups()[1]),
                                 _convert_rule(regex_result.groups()[2], j_suffix).replace("^", "**"))
    if "Expand" in rule_string:
        rule = _parse_strange_rule(rule_string, j_suffix, raw_zero_sectors)
        return sector.SectorRule(_convert_sector_conditions(rule_string[:rule_string.index("] :>")]),
                                 None,
                                 rule[0].replace("^", "**"),
                                 expection_condition=rule[1])
    raise ValueError("invalid rule: %s" % rule_string)


def read_raw_zero_sectors(file_path, j_suffix):
    with open(file_path, 'r') as content_file:
        raw_zero_sectors = _read_raw_zero_sectors(content_file.read(), j_suffix)
        return raw_zero_sectors, _create_zero_rules(raw_zero_sectors)


def x_parse_rules(file_path, j_suffix, raw_zero_sectors):
    j_rules_string = ''.join(map(lambda x: x.rstrip(), open(file_path).readlines()))[2:-1].split(', j')
    for item in j_rules_string:
        rule = _parse_rule(item, j_suffix, raw_zero_sectors)
        if rule is not None:
            yield rule


def main():
    for r in x_parse_rules(sys.argv[1], sys.argv[2]):
        print r

if __name__ == "__main__":
    main()
