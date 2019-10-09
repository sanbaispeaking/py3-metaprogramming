from functools import wraps

def do_stuff(*args, **kwargs):
    """Do your stuff"""
    print('do_stuff')
    print(args, kwargs)

# Yeah we all know that print is the only and true way to debug :>
# But consider that your have dozens of functions to debug, the repetitive log statement 
# will soon become tedious. Remember D.R.Y
# what would you do? You make a decorator

def debug(func):
    msg = func.__qualname__
    def wrapper(*args, **kwargs):
        print(msg)
        return func(*args, **kwargs)
    return wrapper

@debug
def do_stuff_v2(*args, **kwargs):
    """Do your stuff v2"""
    print(args, kwargs)

# But this approach only solve half of the problem,
# The name of decorated function got lost:

print(do_stuff_v2)

# gives you something like `<function debug.<locals>.wrapper at 0x107c901e0>`

def betterdebug(func):
    msg = func.__qualname__
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(msg)
        return func(*args, **kwargs)
    return wrapper

@betterdebug
def do_stuff_v3(*args, **kwargs):
    """Do your stuff v3"""
    print(args, kwargs)

print(do_stuff_v3)

# `wraps` copies metadata, name and docstring, function attributes, etc.,
# if you don't use @wraps, weird things can happen.

# What if you want to debug methods of a class?

class SomeClass:

    def foo(self):
        pass
    
    def bar(self):
        pass

    @classmethod
    def foobar(cls):
        pass

    @staticmethod
    def barfoo():
        pass

# Use decorator syntax for each method is quite annoying.
# As you can imagine, we can decorate them all at once

def debugmethod(cls):
    for name, val in vars(cls).items():
        if callable(val):
            setattr(cls, name, betterdebug(val))

    return cls

SomeClass = debugmethod(SomeClass)
# Or:
#
#   @debugmethod
#   class SomeStuff:
#       ...

# You might have noticed that `classmethod` and `staticmethod` are not wrapped.
# That is because `classmethod` is actually a descriptor.
# When accessing a `classmethod` method on a class, classmethod.__get__(none, Class) is triggered,
# and a bound method is produced by passing the class object as its 2nd arg when called.
# While by accessing a classemthod from `cls.__dict__`, you are bypassing descriptor protocol.

# How you prov it:
assert callable(SomeClass.__dict__['foobar']) is False
assert callable(SomeClass.__dict__['foobar'].__get__(None, SomeClass)) is True

# Moreover, you can access the original func by an special attr of `classmethod`
assert callable(SomeClass.__dict__['foobar'].__func__) is True
# All those above applies to `staticmethod` too.
