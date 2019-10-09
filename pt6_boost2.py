from pt5_boost1 import make_init

# Eliminating signature enforcement, but can we push it further?
# As we can see, the performance of the previous version suffers from stacked `super` invocations.
# For example, to get PosFloat work, Float.__set__ is called to make type check, then Positive.__set__ is called # to make value check, 
# we can use code generation to merge these checks together.
def make__set__(derived):
    code = 'def __set__(self, instance, value):\n'
    # fusion
    for d in derived.__mro__:
        if 'statement__set__' in d.__dict__:
            for statement in d.statement__set__():
                code += '    %s\n' % statement
    return code

# We are gonna need a special classmethod to generate source code,
# so the creation of __set__ should be after that of the class, in another word,
# we are employing __init__ to mod a newly created class.
class DescriptorMeta(type):
    def __init__(self, name, bases, namespace):
        if '__set__' not in namespace:
            code = make__set__(self)
            exec(code, globals(), namespace)
            setattr(self, '__set__', namespace['__set__'])
        else:
            raise NotImplementedError('There is no method to generate __set__ source')


class Descriptor(metaclass=DescriptorMeta):
    def __init__(self, name=None):
        self.name = name

    @staticmethod
    def statement__set__():
        return ('instance.__dict__[self.name] = value',)

    def __delete__(self, instance):
        # del instance.__dict__[self.name]
        raise AttributeError('not allowed')


class Positive(Descriptor):
    @staticmethod
    def statement__set__():
        return ('if value < 0:', '    raise ValueError("Expect a positive value")')


class Typed(Descriptor):
    @staticmethod
    def statement__set__():
        return ('if not isinstance(value, self.expected):', '    raise TypeError("Expected %s" % self.expected)')


class Float(Typed):
    expected = float

class String(Typed):
    expected = str


class PosFloat(Float, Positive):
    pass

print(make__set__(PosFloat))

class AccountMeta(type):
    """Change the formula but keep the flavor"""
    def __new__(mcs, name, bases, namespace):
        fields =  [name for name, v in namespace.items() if isinstance(v, Descriptor)]
        for name in fields:
            namespace[name].name = name

        if fields:
            exec(make_init(*fields), globals(), namespace)

        new_cls = super().__new__(mcs, name, bases, namespace)
        setattr(new_cls, '_fields', fields)
        return new_cls

class AccountBase(metaclass=AccountMeta):
    pass

class Account(AccountBase):
    name = String()
    currency = String()
    balance = PosFloat()


if __name__ == '__main__':
    import timeit
    from pt4_master_of_dot import Account4, SimpleAccount

    assign = "%s.balance = 50.9"
    setup = "from __main__ import %s"
    
    a1 = SimpleAccount('Fred Fuches', 'USD', 0.9)
    a2 = Account4('Fred Fuches', 'USD', 0.9)
    a3 = Account('Fred Fuches', 'USD', 0.9)

    oldschool = timeit.timeit(assign % 'a1', setup % 'a1', number=50000)
    sigmeta = timeit.timeit(assign % 'a2', setup % 'a2', number=50000)
    genmeta = timeit.timeit(assign % 'a3', setup % 'a3', number=50000)
    print(f"Assignment time, oldschool vs oldmeta vs genmeta: {oldschool} vs {sigmeta} vs {genmeta}")
    