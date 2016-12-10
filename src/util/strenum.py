#! /usr/bin/python
# -*- coding: utf-8 -*-

# 定数名はすべて大文字でなければ諸々のメソッドが利用できないので注意すること

import inspect
# from types import MethodType


class Enum(object):

    def __init__(self, *args):
        self._nextIndex = 1
        self.addAll(args)

    def add(self, name):
        """
        @param {string} name 追加したい定数の名前
        """
        setattr(self, name, self._nextIndex)
        self._nextIndex <<= 1
        return self

    def addAll(self, names):
        """
        @param {iterable<string>} names
        """
        for name in names:
            self.add(name)
        return self

    def stringFrom(self, enum):
        """
        定数の値を与えると、定数名が文字列で返ってくる
        与えられた数値が自身の定数でなければNonを返す
        """
        for e in self._elems():
            if e[1] == enum:
                return e[0]
        return None

    def _elems(self):
        """
        Enum変数名、数値のタプルのリスト[('ENUM',8),('CLASS',1),('INTERFACE', 4)]
        """
        attributes = inspect.getmembers(self, lambda a: not(inspect.isroutine(a)))
        return filter(lambda a: not(a[0].startswith('__')) and (a[0].isupper()), attributes)

    def names(self):
        """
        @return {string[]} Enum変数名一覧(ABC順)
        """
        return [e[0] for e in self._elems()]

    def values(self):
        """
        @return {int[]} Enum変数の値一覧(順序はnames()に一致)
        """
        return [e[1] for e in self._elems()]

    def orderedNames(self):
        """
        @return {string[]} Enum変数名一覧(追加した順番)
        """
        return [e[0] for e in sorted(self._elems(), key=lambda t: t[1])]

    def orderedValues(self):
        """
        @return {int[]} Enum変数の値一覧(順序はorderedNames()に一致)
        """
        return [e[1] for e in sorted(self._elems(), key=lambda t: t[1])]

    def get(self, strEnum):
        """
        定数名の文字列からその値を取得する
        Type.get('INCETANCE') == Type.INCETANCEのように、定数名と定数の比較に使用することを想定
        @param {string} strAttr 定数名の文字列
        @return {int} 指定された定数の値
        """
        return getattr(self, strEnum)

    def contains(self, enum, value):
        """
        単一のEnum要素と各Enum要素の論理和を引数に取り、指定された要素が含まれているかのboolean
        Color = Enum(
            'RED',
            'BLUE',
            'YELLOW',
            'GREEN',
            'BLACK',
            'WHITE'
        )
        value = Color.RED | Color.GREEN | Color.BLACK
        print Color.contains(Color.GREEN, value) ==> True
        print Color.contains(Color.BLUE, value) ==> False
        """
        return value & enum > 0


if __name__ == "__main__":
    aaa = Enum(
        'AAA',
        'BBB'
    )
    # print aaa.names()
    Type = Enum(
        'STATIC',
        'ABSTRACT',
        'STRING',
    )
    Type.add('CLASS')
    Type.addAll(['INTERFACE', 'OBJECT', 'ENUM', 'ABSTRACT_CLASS', 'INNER_CLASS'])
    print(Type.stringFrom(Type.INTERFACE))  # INTERFACE
    print(Type.ENUM)  # 64
    print(Type.names())
    print(Type.values())
    print(Type.orderedNames())
    print(Type.orderedValues())
    print(Type.values()[0] == Type.ABSTRACT)
    print(Type.STRING == Type.STRING)
    print(Type.get('STATIC') == Type.STATIC)
    static_inner_class = Type.STATIC | Type.INNER_CLASS
    print(aaa.names())
    print Type.contains(Type.INNER_CLASS, static_inner_class)  # True
    print Type.contains(Type.STATIC, static_inner_class)  # True
    print Type.contains(Type.ABSTRACT, static_inner_class)  # False
