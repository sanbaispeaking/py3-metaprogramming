# Revisit our decorator approach of cls decorator, what if you have
# a bunch of classes to debug? The `@debugmethod` statement appears
# repetitively, that's kind of annoying. Here comes the metadata approach

from pt1_debug_decorator_approach import debugmethod

class DebugMeta(type):
    def __new__(mcs, name, bases, classdict):
        new_cls = super.__new__(mcs, name, bases, classdict)
        new_cls = debugmethod(new_cls)
        return new_cls

# What the fuck is a `type`?
# Every value in python has a type

# >>> type(3)
# <class 'int'>
# >>> type('hello')
# <class 'str'>
# >>> l = [1,2,3,]
# >>> type(l)
# <class 'list'>
# >>>

# A class is a callable that creates instances,
class Shit:
    pass
# and a class itself is an instance of `type`
assert isinstance(Shit, type)
assert isinstance(int, type)
assert isinstance(list, type)

# Let's give the sentences above another thought,
# `type`, is a callable that creates `type` instances which in fact are classes.
# Unlike anyother types, `type` is its own class, a builtin.

# What makes a class?
# Class specifies a scope. And it is the code block within that truly defines a class
class Crab(Shit):    
    def __init__(self, name):
        self.name = name
    def foo(self):
        print('I am Crab.foo')
# The components are:
# name -> 'Crab'
# baseclass -> (Shit,)
# methods -> (__init__, foo)

# How are classes made?
# 1st, you need to isolate class body
body = '''
def __init__(self, name):
    self.name = name
def foo(self):
    print('I am Crab.foo')
'''
# 2nd, create class dictionary
class_dict = type.__prepare__('Crab', (Shit,))
# Class dictionary serves as a local namespace of a class, it holds statements in class body
# 3rd, execute class body, class_dict gets populated
exec(body, globals(), class_dict)
# 4th, assemble, name, bases, and class dictionary(namespace)
Crab = type('Crab', (Shit,), class_dict)
c = Crab('Dude')
c.foo()

# What is metaclass capable of?
# Metaclassed get information of class definitions at the time of **definition**
# So, by employing metaclass, one can:
#   - Inspect data
#   - Modify data
# at the defintion time.

# But why would I use metaclass? Because metaclasses **propagate** down hierarchies, and decorator don't.
# Let's take a closer loot at `DebugMeta`:
#  
# >>> new_cls = super.__new__(mcs, name, bases, classdict)
# >>> new_cls = debugmethod(new_cls)
#
# A new class get created normally, and get decorated immediately after creation
class FuckBase(metaclass=DebugMeta):
    pass

class Fuck(FuckBase):
    pass

class Fucker(Fuck):
    pass
# The debugging get applied across all hierarchy, implicitly.

# Thinking of the big picture:
#   - Decoratores --decorate-> Functions
#   - Class decorators --decorate-> Classes
#   - Metaclasses --infect-> Class hierarchies
