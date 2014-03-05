#!/usr/bin/python
# -*- coding: utf8
"""
https://drive.google.com/file/d/0B1s1OJ-nnslNQ3AzSU9fRDl5VmM/edit?usp=sharing

now it's totally unused
"""

__author__ = 'dima'


import itertools
import swiginac
from rggraphenv import symbolic_functions


class AngularRegularizer(object):
    q = symbolic_functions.var("q")

    def __init__(self, dimensioned_omega):
        self._operation = None
        self.regularize(dimensioned_omega)

    def regularize(self, dimensioned_omega):
        dim = dimensioned_omega.dimension
        dim_int = dim.subs(symbolic_functions.e == 0).to_int()
        series_n = int(- float(dim_int + 1) / 2)
        if series_n < 0:
            series_n = 0
        generator = (swiginac.sin(AngularRegularizer.q)/AngularRegularizer.q) ** dim
        if series_n > 0:
            assert 1 != 1, "TODO"
            series = symbolic_functions.series(generator, AngularRegularizer.q, 0, series_n)
            for degree in xrange(series.ldegree(AngularRegularizer.q), series.rdegree(AngularRegularizer.q)):
                pass
            operation = None
        else:
            operation = IntegrationOperation(generator.subs(AngularRegularizer.q == dimensioned_omega.omega), (0, swiginac.Pi), dimensioned_omega.omega)
        if self._operation is None:
            self._operation = operation
        else:
            self._operation *= operation

    def apply(self, function):
        return self._operation.apply(function)


class RegularizationOperation(object):
    def __add__(self, other):
        return OperationsSum(self, other)

    def __mul__(self, other):
        return OperationsProd(self, other)

    def apply(self, function):
        raise NotImplementedError()

    def composite(self, result_representator):
        raise NotImplementedError()


class OperationsSum(RegularizationOperation):
    def __init__(self, *operations):
        self._operations = tuple(operations)

    def apply(self, function):
        return map(lambda o: o.apply(function), self._operations)

    def composite(self, result_representator):
        return map(lambda o: o.composite(function), self._operations)


class OperationsProd(RegularizationOperation):
    def __init__(self, *operations):
        self._operations = tuple(operations)

    def apply(self, function):
        result = self._operations[0].apply(function) if isinstance(self._operations[0], OperationsSum) else [self._operations[0]]

        for o in self._operations[1:]:
            new_iteration = list()
            for res in result:
                composition = o.composite(res)
                if isinstance(composition, list):
                    result += composition
                else:
                    result.append(composition)
            result = new_iteration

        return result


class IntegrationOperation(RegularizationOperation):
    def __init__(self, weight, limits_tuple, integration_variable):
        self._weight = weight
        self._limits_tuple = limits_tuple
        self._intergration_variable = integration_variable

    def apply(self, function):
        return ResultRepresentator(function * self._weight, integrations=(Integration(self._intergration_variable, limits_tuple),))

    def composite(self, result_representator):
        return result_representator.add_integration(Integration(self._intergration_variable, limits_tuple))


class SubstitutionOperation(RegularizationOperation):
    def __init__(self, substitution_variable, substitution_value):
        self._substitution_variable = substitution_variable
        self._substitution_value = substitution_value

    def apply(self, function):
        return ResultRepresentator(function.subs(self._substitution_variable == self._substitution_value))

    def composite(self, result_representator):
        return result_representator.substitute(self._substitution_variable, self._substitution_value)


class Integration(object):
    def __init__(self, integration_variable, integration_limits):
        self._integration_variable = integration_variable
        self._integrations_limits = integration_limits

    @property
    def integration_variable(self):
        return self._integration_variable

    @property
    def integration_value(self):
        return self._integration_value


class ResultRepresentator(object):
    def __init__(self, function, integrations=tuple()):
        self._function = function
        self._integrations = tuple(integrations)

    @property
    def function(self):
        return self._function

    @property
    def integrations(self):
        return self._integrations

    def add_integration(self, integration):
        return ResultRepresentator(self._function, self._integrations + (integration, ))

    def substitute(self, variable, value):
        return ResultRepresentator(self._function.subs(variable == value), self._integrations)


def main():
    import spherical_coordinats
    dimensioned_omega = spherical_coordinats.DimensionedOmega(omega=symbolic_functions.var("omega"), dimension=symbolic_functions.D)
    AngularRegularizer(dimensioned_omega)


if __name__ == "__main__":
    main()