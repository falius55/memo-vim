#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import vim


class Tab(object):
    DEFAULT_KEY = 'default_key'

    def __init__(self, tab, vim):
        vim.appendTab(self)
        self._tab = tab
        self._vim = vim
        self._tag = {}

    def elem(self):
        return self._tab

    def setTag(self, key=None, tag=None):
        if key is None and tag is None:
            raise ValueError
        if key is None or tag is None:
            self._tag[Tab.DEFAULT_KEY] = key if tag is None else tag
            return
        self._tag[key] = tag

    def getTag(self, key=None, defaultIfNotFound=None):
        if key is None:
            return self._tag.get(Tab.DEFAULT_KEY, defaultIfNotFound)
        return self._tag.get(key, defaultIfNotFound)

    def getNumber(self):
        return self._tab.number

    def findWindows(self):
        return [self._vim.find(e) for e in self._tab.windows]

    def isExist(self):
        for tabElem in vim.tabpages:
            if tabElem == self._tab:
                return True
        else:
            return False

    def getVar(self, varName, defaultIfNotFound=None):
        """
        t:変数
        """
        if defaultIfNotFound is None:
            return self._tab.vars.get(varName)
        return self._tab.vars.get(varName, defaultIfNotFound)

    def getCurrentWindow(self):
        return self._vim.find(self._tab.window)

    def __eq__(self, another):
        """
        vim標準との比較でも、同じタブを指していればTrueを返す
        """
        if isinstance(another, Tab):
            return self is another
        elif isinstance(another, vim.TabPage):
            return self._tab is another
        return False

    def __hash__(self):
        return hash(self._tab)
