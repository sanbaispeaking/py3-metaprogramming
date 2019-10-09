# Have your ever found youself write bunches of boilerplate __init__ methods?
#
# class Host:
#     def __init__(self, hostname, port,):
#         self.hostname = hostname
#         ...
#
# class Student:
#     def __init__(self, name, address, email):
#         self.name = name
#          ...
#
# That is not DRY enough

class Fielded:
    _fields = []
    def __init__(self, *args):
        if len(args) != len(self._fields):
            raise TypeError('Invalid args #')
        for name, value in zip(self._fields, args):
            setattr(self, name, value)

class Host(Fielded):
    _fields = ['hostname', 'port']

class Student(Fielded):
    _fields = ['name', 'address', 'email']

# We generalize the __init__ method, but we also lost support of kwargs:
#
# >>> Host('fuck@fuck.fuck', port=90)
# ...
# TypeError: __init__() got an unexpected keyword argument 'port'
# 
# That is because we don't have the right **signature**

# In Python3, you can create signautre object, and bind args & kwargs passed into a function 
# to that signature
from inspect import Parameter, Signature

def make_signature(names):
    return Signature(
        Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) 
        for name in names)

class Signatured:
    _signature = make_signature([])
    def __init__(self, *args, **kwargs):
        bound_sig = self._signature.bind(*args, **kwargs)
        for name, value in bound_sig.arguments.items():
            setattr(self, name, value)

class SigStudent(Signatured):
    _signature = make_signature(['name', 'address', 'email'])

ss = SigStudent('Fred.Fuches', address='LA', email='fuches@fuck.fuck')
# print(ss.name, ss.address, ss.email)

# Bindings happen at runtime, so it is not possible to make binding outside __init__
# As we have learned previously that there are 2 possible ways to generalize this
# signature problem:
#   - The cls decorator approach:
def add_signature(*names):
    def decorator(cls):
        cls._signature =  make_signature(names)
        return cls
    return decorator

# Use class::`Signatured` as a pivot point
@add_signature('name', 'currency', 'balance')
class Account(Signatured):
    pass

ac = Account('Mr.Fuches', currency='fuck', balance='shit')
print(ac.name, ac.currency, ac.balance)

#   - Metaclass approach:
class SigMeta(type):
    def __new__(cls, name, bases, namespace):
        new_cls = super().__new__(cls, name, bases, namespace)
        sig = make_signature(new_cls._fields)
        setattr(new_cls, '_signature', sig)
        return new_cls

class SigBase(metaclass=SigMeta):
    _fields = []
    def __init__(self, *args, **kwargs):
        bound_sig = self._signature.bind(*args, **kwargs)
        for name, val in bound_sig.arguments.items():
            setattr(self, name, val)

class Point(SigBase):
    _fields = ['x', 'y']

# Now everything is back to original 'simple' solution, signatures are created behind scenes.

# A bit off topic, it is OK to replace `_signature` with either `__signature__` or `_signature`,
# but never `__signature`, otherwise the interpreter keeps yelling.
# -- RESERVED AS A EXERCISE FOR THE READERS --
# Hint: Name mangling, use dis.dis(cls.__init__) you will see.

# Some showerthoughts:
# If your goal is to add some functionality to separete, unrelated classes, use class decorators;
# If you are trying to perform actions in combination with inheritance, use metaclass;
# And remember all these tools are meant to work together.
