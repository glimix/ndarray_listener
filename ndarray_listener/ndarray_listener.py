r"""
*****
Usage
*****
"""
from numpy import asarray, ndarray


class ndarray_listener(ndarray):
    r"""

    Examples
    --------

    A scalar is stored as a zero-dimensional array much like a NumPy scalar:

    .. doctest::

        >>> from __future__ import print_function
        >>> from ndarray_listener import ndarray_listener
        >>> from numpy import atleast_1d
        >>>
        >>> class Watcher(object):
        ...     def __init__(self, msg):
        ...         self._msg = msg
        ...
        ...     def __call__(self, value):
        ...         print(self._msg + " called with %s" % str(value))
        ...
        >>> scalar = ndarray_listener(-0.5)
        >>>
        >>> you0 = Watcher("First guy")
        >>> you1 = Watcher("Second guy")
        >>>
        >>> scalar.talk_to(you0)
        >>> scalar.itemset(-1.0)
        First guy called with -1.0
        >>> s0 = scalar.copy()
        >>> s0.itemset(-0.5)
        First guy called with -0.5
        >>> s0.talk_to(you1)
        >>> scalar.itemset(0.0)
        First guy called with 0.0
        Second guy called with 0.0
        >>>
        >>> s1 = atleast_1d(scalar)
        >>> s1[0] = 1.0
        First guy called with [ 1.]
        Second guy called with [ 1.]

    One-dimension arrays are also supported:

    .. doctest::

        >>> from ndarray_listener import ndarray_listener
        >>> from numpy import atleast_1d
        >>>
        >>> vector = ndarray_listener([-0.5, 0.1])
        >>>
        >>> you0 = Watcher("First guy")
        >>> you1 = Watcher("Second guy")
        >>>
        >>> vector.talk_to(you0)
        >>>
        >>> vector[0] = 0.0
        First guy called with [ 0.   0.1]
        >>> vector[:] = 1.0
        First guy called with [ 1.  1.]
        >>>
        >>> v0 = vector.copy()
        >>> v0.itemset(0, 1.1)
        First guy called with [ 1.1  1. ]
        >>>
        >>> v0.itemset(1, 2.2)
        First guy called with [ 1.1  2.2]
        >>>
        >>> v1 = v0.ravel()
        >>>
        >>> v1.talk_to(you1)
        >>> vector[-1] = 9.9
        First guy called with [ 1.   9.9]
        Second guy called with [ 1.   9.9]
    """

    def __new__(cls, input_array):
        obj = asarray(input_array).view(cls)

        if hasattr(input_array, '_listeners'):
            obj._listeners = input_array._listeners
        else:
            obj._listeners = []

        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._listeners = getattr(obj, '_listeners', [])

    def __setslice__(self, *args, **kwargs):
        super(ndarray_listener, self).__setslice__(*args, **kwargs)
        self.__notify()

    def __setitem__(self, *args, **kwargs):
        super(ndarray_listener, self).__setitem__(*args, **kwargs)
        self.__notify()

    def __setattr__(self, *args, **kwargs):
        super(ndarray_listener, self).__setattr__(*args, **kwargs)
        if len(args) > 0 and args[0] == '_listeners':
            return
        self.__notify()

    def __getitem__(self, *args, **kwargs):
        v = super(ndarray_listener, self).__getitem__(*args, **kwargs)
        if isinstance(v, ndarray_listener):
            return v

        v = ndarray_listener(v)
        for l in self._listeners:
            v.talk_to(l)
        return v

    def talk_to(self, me):
        self._listeners.append(me)

    def __notify(self):
        for l in self._listeners:
            l(asarray(self))

    def itemset(self, *args, **kwargs):
        super(ndarray_listener, self).itemset(*args, **kwargs)
        self.__notify()
