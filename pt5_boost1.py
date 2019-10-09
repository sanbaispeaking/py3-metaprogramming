from pt4_master_of_dot import Descriptor, PosFloat, String, SimpleAccount, Account4

# The reasons why our metaclass sucks ass are that signature enforcement
# as well as multiple inheritance.
# There is no way to get signature bound prior to __init__ get called, I told you so.
# In fact, we really don't need that signature.
def make_init(*fields):
    code = f'def __init__(self, {", ".join(fields)}):\n'
    for name in fields:
        code += f'    self.{name} = {name}\n'
    return code

if __name__ == '__main__':
    print(make_init('shit', 'fuck', 'crab'))
# The generated code seems legit.

class AccountMeta(type):
    """Change the formula but keep the flavor"""
    def __new__(mcs, name, bases, namespace):
        fields =  [name for name, v in namespace.items() if isinstance(v, Descriptor)]
        for name in fields:
            namespace[name].name = name

        if fields:
            exec(make_init(*fields), globals(), namespace)

        new_cls = super().__new__(mcs, name, bases, namespace)
        # No signature reinforcement, but preserve for code that wants field names.
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

    instantiation = "a = %s('Fred Fuches', 'USD', 50.9)"
    setup = "from __main__ import %s"
    
    oldschool = timeit.timeit(instantiation % 'SimpleAccount', setup % 'SimpleAccount', number=50000)
    sigmeta = timeit.timeit(instantiation % 'Account4', setup % 'Account4', number=50000)
    genmeta = timeit.timeit(instantiation % 'Account', setup % 'Account', number=50000)
    print(f"Instance creation time, oldschool vs oldmeta vs genmeta: {oldschool} vs {sigmeta} vs {genmeta}")
