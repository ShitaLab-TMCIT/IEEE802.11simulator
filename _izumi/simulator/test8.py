class Test:
    _queue = []

    def __init__(self):
        self._a = 1


    def wrapper(func):
        def _(self,*args,**kwargs):
            self._queue.append(lambda:func(self,*args,**kwargs))
        return _

    @property
    def a(self):
        return self._a


    @a.setter
    @wrapper
    def a(self,value):
        self._a = value


    def update(self):
        for i in self._queue:
            i()
        self._queue.clear()



test = Test()
print(test.a)
test.a = 2
print(test.a)
test.update()
print(test.a)


