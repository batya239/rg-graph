#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import rggraphenv
import inject
import common
import graphine


class Configure(object):
    def __init__(self):
        self._calculators_holder = None
        self._k_operation = None
        self._uv_filter = None
        self._ir_filter = None
        self._storage_holder = None
        self._dimension = None
        self._space_dimension = None
        self._space_dimension_int = None

    def with_dimension(self, dimension):
        self._dimension = dimension
        self._space_dimension = dimension.subs(rggraphenv.symbolic_functions.e == 0)
        self._space_dimension_int = self._space_dimension.to_int()
        return self

    def with_calculators(self, *calculators):
        self._calculators_holder = rggraphenv.GraphCalculatorManager(*calculators)
        return self

    def with_k_operation(self, k_operation):
        self._k_operation = k_operation
        return self

    def with_uv_filter(self, uv_relevance_condition):
        self._uv_filter = graphine.filters.is_relevant(uv_relevance_condition)
        return self

    def with_ir_filter(self, ir_relevance_condition):
        self._ir_filter = (graphine.filters.connected + graphine.filters.is_relevant(ir_relevance_condition))
        return self

    def with_storage_holder(self, storage_setting):
        self._storage_holder = rggraphenv.StorageHolder(storage_setting)
        return self

    @classmethod
    def k_operation(cls):
        return inject.instance("k_operation")

    @classmethod
    def uv_filter(cls):
        return inject.instance("uv_filter")

    @classmethod
    def ir_filter(cls):
        return inject.instance("ir_filter")

    @classmethod
    def storage(cls):
        return inject.instance(rggraphenv.StorageHolder)

    def configure(self):
        def injector(binder):
            binder.bind(rggraphenv.GraphCalculatorManager, self._calculators_holder)
            binder.bind(rggraphenv.StorageHolder, self._storage_holder)
            binder.bind(common.AbstractKOperation, self._k_operation)
            binder.bind("uv_filter", self._uv_filter)
            binder.bind("ir_filter", self._ir_filter)
            binder.bind("k_operation", self._k_operation)
            binder.bind("dimension", self._dimension)
            binder.bind("space_dimension", self._space_dimension)
            binder.bind("space_dimension_int", self._space_dimension_int)

        inject.configure(injector)

    @classmethod
    def clear(cls):
        inject.clear()