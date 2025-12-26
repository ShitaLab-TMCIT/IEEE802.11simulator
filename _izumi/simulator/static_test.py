class A:
    Null : 'A' = None

    def __init__(self):
        self.b = B.Null

class B:
    Null : 'B' = None
    def __init__(self):
        self.a = A.Null

A.Null = A()
B.Null = B()
A.Null.b = B.Null
B.Null.a = A.Null
