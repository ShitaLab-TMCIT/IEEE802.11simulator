class TestClass:
    _value : int

    @property
    def value(self) -> int:
        return self._value


TestClass.value
