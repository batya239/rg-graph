#!/usr/bin/python
# -*- coding: utf8

__author__ = ['mkompan', 'dima']

import re
import sector
import scalar_product
from rggraphenv import symbolic_functions

_SECTOR_REGEXP = re.compile("^\[(.*)\] /; (.*) -> (.*)$")
_SECTOR_CONDITION_REGEXP = re.compile(".*n(.+)_\)\?(.+)")
_EXPAND_REGEXP = re.compile(".*Expand\[(.*)$")
_JS_REGEXP = re.compile("(js[^\]]+\])")
_SECTOR_SECTOR_REGEXP = re.compile("(Sector[^\)]+\))")
_PROPAGATORS_REGEXP = re.compile("Ds\[[^\{]+\{([^\}]+)\}")
_MIS_REGEXP = re.compile("MIs[^\{]+\{([^\}]+)\}")
_NUMERATORS_REGEXP = re.compile("Toj[^\{]+\{([^\}]+)\}")
_DEBUG = False


def parse_master_sectors(file_path):
    with open(file_path, 'r') as f:
        pass


def parse_scalar_products_reducing_rules(file_path, j_suffix, loop_momentum_sign):
    import swiginac
    with open(file_path, 'r') as f:
        content = "".join(f.readlines())
        content = content.replace("\n", "")
        rules = dict()
        raw_extracted = _NUMERATORS_REGEXP.findall(content)[0]
        raw_extracted = raw_extracted.replace(" ", "")[2:]
        for raw_numerator in raw_extracted.split(",sp"):
            raw_numerator = raw_numerator.strip()
            raw_numerator = raw_numerator.replace("j[%s," % j_suffix, "sector.Sector(")
            raw_numerator = raw_numerator.replace("]", ")")
            raw_numerator = raw_numerator.replace("^", "**")
            raw_key, raw_rule = raw_numerator.split("->")
            raw_key = raw_key[1:-1]
            raw_kp = raw_key.split(",")
            kp = list()
            for p in raw_kp:
                if p.startswith(loop_momentum_sign):
                    kp.append(int(p[1:]))
                else:
                    kp.append(0)
            key = scalar_product.ScalarProductRuleKey(*kp)
            raw_rule = symbolic_functions.to_internal_code(raw_rule, strong=True)
            rules[key] = eval(raw_rule)
        return rules


def _read_raw_zero_sectors(zero_sectors_string, j_suffix):
    _zero_sectors_string = zero_sectors_string[1: -2]
    return set(map(lambda s: s.replace("js[%s, " % j_suffix, "Sector(").replace("]", ")"),
                   _JS_REGEXP.findall(_zero_sectors_string)))


def _create_zero_rules(raw_zero_sectors):
    result = set()
    for rs in raw_zero_sectors:
        propagators = list()
        for e in eval(rs[6:]):
            if e == 1:
                propagators.append(sector.SectorRuleKey.PROPAGATOR_CONDITION_POSITIVE)
            else:
                propagators.append(sector.SectorRuleKey.PROPAGATOR_CONDITION_NOT_POSITIVE)
        result.add(sector.SectorRuleKey(propagators))
    return result


def convert_rule(rule_string, j_suffix):
    result = re.sub("j\[([^,\]]+),([^\]]+)\]", "j_\\1(\\2)", rule_string)
    result = re.sub("\s+", " ", result)
    result = result.replace("j_%s" % j_suffix, "Sector")
    result = _replace_n(result)
    result = re.sub('([\d]+)\\*', 'swiginac.numeric(str(\\1))*', result)
    result = re.sub('\\*\\(\\{([\d]+)\\}\\)', '*swiginac.numeric(str({\\1}))', result)
    result = result.replace(" ", "")
    result = re.sub('([\(\+\*-/])([\d]+)','\\1swiginac.numeric(\'\\2\')', result)
    result = re.sub('([\d]+)([\(\+\*-/])','swiginac.numeric(\'\\1\')\\2', result)
    result = re.sub('([\(\+\*-/])([\d]+)([\)\+\*-/])','\\1swiginac.numeric(\'\\2\')\\3', result)
    return result


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


def _parse_strange_rule(rule_string, j_suffix):
    _rule_string = _EXPAND_REGEXP.match(rule_string)
    _rule_string = _rule_string.groups()
    if not _rule_string or not len(_rule_string):
        raise ValueError(_rule_string)
    _rule_string = _rule_string[0]
    _rule_string = re.sub("j\[([^,]+),([^\]]+)\]", "j_\\1(\\2)", _rule_string)
    _rule_string = _rule_string.replace("j_%s" % j_suffix, "Sector")
    _rule_string = _replace_n(_rule_string)
    _rule_string = re.sub('([\d]+)\\*', 'swiginac.numeric(str(\\1))*', _rule_string)
    _rule_string = re.sub('\\*\\(\\{([\d]+)\\}\\)', '*swiginac.numeric(str({\\1}))', _rule_string)
    _rule_string = _rule_string.replace(" ", "")
    _rule_string = re.sub('([\(\+\*-/])([\d]+)','\\1swiginac.numeric(\'\\2\')', _rule_string)
    _rule_string = re.sub('([\d]+)([\(\+\*-/])','swiginac.numeric(\'\\1\')\\2', _rule_string)
    _rule_string = re.sub('([\(\+\*-/])([\d]+)([\)\+\*-/])','\\1swiginac.numeric(\'\\2\')\\3', _rule_string)
    return _rule_string


def _convert_sector_conditions(sector_condition_string):
    result = list()
    vars_string = sector_condition_string.split(',')[1:]
    for item in vars_string:
        regex_result = _SECTOR_CONDITION_REGEXP.match(item)
        if regex_result:
            n, value = regex_result.groups()
            value = value.rstrip()
            if value == 'Positive':
                result.append(sector.SectorRuleKey.PROPAGATOR_CONDITION_POSITIVE)
            elif value == 'NonPositive':
                result.append(sector.SectorRuleKey.PROPAGATOR_CONDITION_NOT_POSITIVE)
            else:
                raise AssertionError("%s is incorrect sector condition" % value)
    return result


def _parse_additional_condition(condition_string):
    raw_result = condition_string.replace("||", "or").replace("&&", "and").replace("!(", "not (")
    raw_result = re.sub("\s+", " ", raw_result)
    raw_result = _replace_n(raw_result)
    return raw_result


def _replace_n(string):
    return re.sub('n(\d+)', '({\\1})', string)


def _parse_rule(rule_string, j_suffix, parse_symmetry=False):
    regex_result = _SECTOR_REGEXP.match(rule_string)
    if regex_result:
        sector_rule = sector.SectorRule(_parse_additional_condition(regex_result.groups()[1]),
                                        convert_rule(regex_result.groups()[2], j_suffix).replace("^", "**")[:-2] if parse_symmetry else convert_rule(regex_result.groups()[2], j_suffix).replace("^", "**"))
        return sector.SectorRuleKey(_convert_sector_conditions(regex_result.groups()[0])), \
            sector_rule
    if "Expand" in rule_string:
        rule = _parse_strange_rule(rule_string, j_suffix)
        if parse_symmetry:
            rule = rule[:-2]
        return sector.SectorRuleKey(_convert_sector_conditions(rule_string[:rule_string.index("] :>")])), \
            sector.SectorRule(None, rule.replace("^", "**"))
    raise ValueError("invalid rule: %s" % rule_string)


def read_raw_zero_sectors(file_path, j_suffix):
    with open(file_path, 'r') as content_file:
        raw_zero_sectors = _read_raw_zero_sectors(content_file.read(), j_suffix)
        return raw_zero_sectors, _create_zero_rules(raw_zero_sectors)


def x_parse_rules(file_path, j_suffix, parse_symmetry=False):
    j_rules_string = ''.join(map(lambda x: x.rstrip(), open(file_path).readlines()))[2:-1].split(', {j' if parse_symmetry else ', j')
    first = True
    for item in j_rules_string:
        if parse_symmetry and first:
            first = False
            continue
        yield _parse_rule(item, j_suffix, parse_symmetry)


def parse_masters(file_path, j_suffix):
    with open(file_path, 'r') as f:
        content = "".join(f.readlines())
        content = content.replace("\n", "")
        sectors = set()
        for raw_sector in _MIS_REGEXP.findall(content)[0].split("],"):
            raw_sector = raw_sector.strip()
            raw_sector = raw_sector.replace("j[%s," % j_suffix, "sector.Sector(")
            raw_sector = raw_sector[:-1] if raw_sector.endswith("]") else raw_sector
            sectors.add(eval(raw_sector + ")"))
        return sectors


def parse_propagators(file_path, loops_count, loop_momentum_sign, external_momentum_sign):
    propagator_variables = [external_momentum_sign]
    for i in xrange(1, loops_count + 1):
        propagator_variables.append(loop_momentum_sign + str(i))
    propagators = dict()
    with open(file_path, 'r') as f:
        content = "".join(f.readlines())
        content = content.replace("\n", "")
        raw_result = _PROPAGATORS_REGEXP.findall(content)[0]
        raw_result = raw_result.split(",")
        j = 0
        for i in xrange(1, len(raw_result), 2):
            raw_propagator = raw_result[i][:-1].replace(" ", "")
            propagator_as_list = list()
            for variable in propagator_variables:
                index = raw_propagator.find(variable)
                if index != -1:
                    sign = 1 if index == 0 or raw_propagator[index - 1] == "+" else - 1
                    propagator_as_list.append(sign)
                else:
                    propagator_as_list.append(0)
            propagators[j] = tuple(propagator_as_list)
            j += 1
    return propagators