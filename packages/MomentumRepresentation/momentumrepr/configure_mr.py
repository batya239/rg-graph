__author__ = 'dima'


from rggraphenv import symbolic_functions
import inject


class Configure(object):
    def __init__(self):
        self._dimension = None
        self._space_dimension_int = None
        self._target_loops_count = None
        self._debug = False

    def with_dimension(self, dimension):
        self._dimension = dimension
        self._space_dimension_int = dimension.subs(symbolic_functions.e == 0).to_int()
        return self

    def with_target_loops_count(self, target_loops_count):
        self._target_loops_count = target_loops_count
        return self

    def with_debug(self, debug):
        self._debug = debug
        return self

    def configure(self):
        def injector(binder):
            binder.bind("dimension", self._dimension)
            binder.bind("space_dimension_int", self._space_dimension_int)
            binder.bind("target_loops_count", self._target_loops_count)
            binder.bind("debug", self._debug)

        inject.configure(injector)

    @classmethod
    def debug(cls):
        return inject.instance("debug")

    @classmethod
    def target_loops_count(cls):
        return inject.instance("target_loops_count")

    @classmethod
    def dimension(cls):
        return inject.instance("dimension")

    @classmethod
    def space_dimension_int(cls):
        return inject.instance("space_dimension_int")

    @classmethod
    def clear(cls):
        inject.clear()
