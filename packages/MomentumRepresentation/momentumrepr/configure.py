__author__ = 'dima'


from rggraphenv import symbolic_functions
import inject


class Configure(object):
    def __init__(self):
        self._dimension = None
        self._space_dimension_int = None

    def with_dimension(self, dimension):
        self._dimension = dimension
        self._space_dimension_int = dimension.subs(symbolic_functions.e == 0).to_int()
        return self

    def configure(self):
        def injector(binder):
            binder.bind("dimension", self._dimension)
            binder.bind("space_dimension_int", self._space_dimension_int)

        inject.configure(injector)

    @classmethod
    def dimension(cls):
        return inject.instance("dimension")

    @classmethod
    def space_dimension_int(cls):
        return inject.instance("space_dimension_int")

    @classmethod
    def clear(cls):
        inject.clear()
