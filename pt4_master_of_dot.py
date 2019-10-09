# Type is like a duck, and rhymes with ...

# For programmers using dynamic typing languages, type checking sometimes 
# can be really a pain in the ass. If you don't it properly, you are most likely
# to waste too much time on debugging type errors caused by trivial misstakes.

# There are 2 kinds of checks:
#   - type checking;
#   - validation: >, <, ==, etc.
# You can upgrade attributes to properties:
import timeit
from collections import OrderedDict
from pt3_bind_sig import SigBase, make_signature

class Account(SigBase):
    _fields = ('name', 'currency', 'balance')

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, val):
        if not isinstance(val, str):
            raise TypeError('expect str')
        if not val:
            raise ValueError('could not be empty')
        self._name = val

# And it works, but it quickly get annoying.
# Imagine you are writting same code for many attributes, you are repeating yourself.
# How do we structure it? Let's take a closer look at `property`
# Property is implemented by descriptor 
# 
# And descriptor customize how you access attributes.
class Descriptor:
    """A basic descriptor"""
    def __init__(self, name=None):
        self.name = name
    
    # def __get__(self, instance, cls):
    #     if instance is None:
    #         return self
    #     else:
    #         return instance.__dict__[self.name]
        
    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        # del instance.__dict__[self.name]
        raise AttributeError('not allowed')
# Moreover, if it merely returns values from class dict, you don't even need the __get__
class Account1(SigBase):
    _fields = ('name', 'currency', 'balance')

    name = Descriptor('name')
    currency = Descriptor('currency')
    balance = Descriptor('balance')

a = Account1(name='Fred Fuches', currency='USD', balance=42)
# When we access attribute `balance` by dot operator, it get captured and translated
# into something like
a.balance = 50
Account1.__dict__['balance'].__set__(a, 50)
#
# >>> try:
# >>>     del a.balance
# >>> except AttributeError:
# >>>     print('Can not delete')
#

# Add type checking
class Typed(Descriptor):
    expected = object
    def __set__(self, instance, value):
        if not isinstance(value, self.expected):
            raise TypeError('Expected %s'  % self.expected)
        # Yeh, in python3, you never need to pass `class` or `self` into super nomore.
        super().__set__(instance, value)

class Float(Typed):
    expected = float

class String(Typed):
    expected = str

class Account2(SigBase):
    _fields = ('name', 'currency', 'balance')

    name = String('name')
    currency = String('currency')
    balance = Float('balance')
# 
# >>> try:
# >>>     a = Account2('Fred Fuches', 'USD', '50')
# >>> except TypeError:
# >>>     print('Got you')
#

class Positive(Descriptor):
    def __set__(self, instance, value):
        if value < 0:
            raise ValueError('Expect a positive value')
        super().__set__(instance, value)

# Use as mixin class
class PosFloat(Float, Positive):
    pass

class Account3(SigBase):
    _fields = ('name', 'currency', 'balance')

    name = String('name')
    currency = String('currency')
    balance = PosFloat('balance')
# The order of base classes is fairly important,
if __name__ == '__main__':
    print(PosFloat.__mro__)
# the mro class chain determines the order in which the value is checked by different __set__

# As you see, there is still quite a bif of reptition: _fields, and x = Cls('x') stuff
# why don't we just use keys from class dict as attribute names?
# Push it a bit further:
class StructureMeta(type):
    @classmethod
    def __prepare__(cls, name, bases):
        """Creates and returns dict to use for body execution,
        And OrderedDict will preserve the definition order
        """
        return OrderedDict()

    def __new__(cls, name, bases, namespace):
        fields = [k for k, v in namespace.items() if isinstance(v, Descriptor)]
        for name in fields:
            namespace[name].name = name # equivlent to name = Descriptor(name='name')
        new_cls = super().__new__(cls, name, bases, dict(namespace))
        sig = make_signature(fields)
        setattr(new_cls, '_signature', sig)
        return new_cls

class Structure(metaclass=StructureMeta):
    def __init__(self, *args, **kwargs):
        bound_sig = self._signature.bind(*args, **kwargs)
        for name, value in bound_sig.arguments.items():
            setattr(self, name, value)

class Account4(Structure):
    name = String()
    currency = String()
    balance = PosFloat()

if __name__ == '__main__':
    a = Account4('Fred Fuches', 'USD', 50.9)
    print(f'{a.name} has {a.currency} {a.balance}')
# F-sting is way faster and more readable than either % or str.format()

# Everything works! That is awesome!
# But...
# What is the price?
class SimpleAccount:

    def __init__(self, name, currency, balance):
        self.name = name
        self.currency = currency
        self.balance = balance

sa = SimpleAccount('Fred Fuches', 'USD', 50.9)


if __name__ == '__main__':
    simple = timeit.timeit("a = SimpleAccount('Fred Fuches', 'USD', 50.9)", "from __main__ import SimpleAccount", number=50000)
    fancy = timeit.timeit("a = Account4('Fred Fuches', 'USD', 50.9)", "from __main__ import Account4", number=50000)
    print(f"Instance creation time, simple vs fancy: {simple} vs {fancy}")
    
    simple = timeit.timeit("sa.balance = 50.9", "from __main__ import sa", number=50000)
    fancy = timeit.timeit("a.balance = 50.9", "from __main__ import a", number=50000)
    print(f"Attr assignment time, simple vs fancy: {simple} vs {fancy}")
    # Oh god, that sucks ass.

    simple = timeit.timeit("sa.balance", "from __main__ import sa", number=50000)
    fancy = timeit.timeit("a.balance", "from __main__ import a", number=50000)
    print(f"Attr access time, simple vs fancy: {simple} vs {fancy}") 