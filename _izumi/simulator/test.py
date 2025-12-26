class MyClass:
    def __init__(self):
        self._value = 0

    @property
    def value(self) -> int: # プロパティがintを返すことをヒント
        """値を取得するプロパティ"""
        return self._value

    @value.setter
    def value(self, new_value: int): # セッターの引数と返り値（None）にヒント
        """値を設定するプロパティ"""
        if new_value < 0:
            raise ValueError("値は負であってはなりません")
        self._value = new_value

# 使用例
obj = MyClass()
obj.value
print(obj.value) # 10
# obj.value = "hello" # mypyでエラーになる
