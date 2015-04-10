__author__ = 'dima'


from rggraphenv import symbolic_functions
import inject
from polynomial.eps_number import epsNumber


class Configure(object):
    INTEGRATION_ALGORITHM_CODES = {
        "vegas": 0,
        "suave": 1,
        "devonne": 2,
        "cuhre": 3
    }

    def __init__(self):
        self._dimension = None
        self._space_dimension_int = None
        self._target_loops_count = None
        self._debug = False
        self._integration_algorithm = Configure.INTEGRATION_ALGORITHM_CODES["suave"]
        self._maximum_points_number = 2000
        self._relative_error = 10e-4
        self._absolute_error = 10e-5
        self._delete_integration_tmp_dir_on_shutdown = True
        self._do_d_tau = True

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

    def with_integration_algorithm(self, integration_algorithm):
        code = Configure.INTEGRATION_ALGORITHM_CODES.get(integration_algorithm, None)
        if code is None:
            try:
                code = eval(integration_algorithm)
            except:
                pass
        if code is None:
            raise Exception("no integration algorithm for name - %s" % integration_algorithm)
        self._integration_algorithm = code
        return self

    def with_maximum_points_number(self, maximum_points_number):
        self._maximum_points_number = maximum_points_number
        return self

    def with_relative_error(self, relative_error):
        self._relative_error = relative_error
        return self

    def with_absolute_error(self, absolute_error):
        self._absolute_error = absolute_error
        return self

    def with_delete_integration_tmp_dir_on_shutdown(self, delete_integration_tmp_dir_on_shutdown):
        self._delete_integration_tmp_dir_on_shutdown = delete_integration_tmp_dir_on_shutdown
        return self

    def with_do_d_tau(self, do_d_tau):
        self._do_d_tau = do_d_tau
        return self

    def configure(self):
        def injector(binder):
            binder.bind("dimension", self._dimension)
            binder.bind("space_dimension_int", self._space_dimension_int)
            binder.bind("target_loops_count", self._target_loops_count)
            binder.bind("debug", self._debug)
            binder.bind("integration_algorithm", self._integration_algorithm)
            binder.bind("maximum_points_number", self._maximum_points_number)
            binder.bind("relative_error", self._relative_error)
            binder.bind("absolute_error", self._absolute_error)
            binder.bind("delete_integration_tmp_dir_on_shutdown", self._delete_integration_tmp_dir_on_shutdown)
            binder.bind("do_d_tau", self._do_d_tau)

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
    def dimension_pair(cls):
        dim = cls.dimension()
        a = dim.subs(symbolic_functions.e == 0).to_int()
        b = 0#dim.coeff(symbolic_functions.e).to_int()
        return epsNumber((a, b))

    @classmethod
    def space_dimension_int(cls):
        return inject.instance("space_dimension_int")

    @classmethod
    def integration_algorithm(cls):
        return inject.instance("integration_algorithm")

    @classmethod
    def maximum_points_number(cls):
        return inject.instance("maximum_points_number")

    @classmethod
    def relative_error(cls):
        return inject.instance("relative_error")

    @classmethod
    def absolute_error(cls):
        return inject.instance("absolute_error")

    @classmethod
    def delete_integration_tmp_dir_on_shutdown(cls):
        return inject.is_configured() and inject.instance("delete_integration_tmp_dir_on_shutdown")

    @classmethod
    def do_d_tau(cls):
        return inject.instance("do_d_tau")

    @classmethod
    def clear(cls):
        inject.clear()
