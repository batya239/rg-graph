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

    def with_dimension(self, dimension):
        self._dimension = dimension
        self._space_dimension = dimension.subs(rggraphenv.symbolic_functions.e == 0)
        return self

    def with_calculators(self, *calculators):
        self._calculators_holder = rggraphenv.GraphCalculatorManager(*calculators)
        return self

    def with_k_operation(self, k_operation):
        self._k_operation = k_operation
        return self

    def with_uv_filter(self, uv_relevance_condition):
        self._uv_filter = graphine.filters.isRelevant(uv_relevance_condition)
        return self

    def with_ir_filter(self, ir_relevance_condition):
        self._ir_filter = (graphine.filters.connected + graphine.filters.isRelevant(ir_relevance_condition))
        return self

    def with_storage_holder(self, storage_setting):
        self._storage_holder = rggraphenv.StoragesHolder(storage_setting)
        return self

    def configure(self):
        this = self

        def injector(binder):
            binder.bind(rggraphenv.GraphCalculatorManager, this._calculators_holder)
            binder.bind(rggraphenv.StoragesHolder, this._storage_holder)
            binder.bind(common.AbstractKOperation, this._k_operation)
            binder.bind("uv_filter", this._uv_filter)
            binder.bind("ir_filter", this._ir_filter)
            binder.bind("k_operation", this._k_operation)
            binder.bind("dimension", this._dimension)
            binder.bind("space_dimension", this._space_dimension)

        inject.configure(injector)

    @classmethod
    def clear(cls):
        inject.clear()