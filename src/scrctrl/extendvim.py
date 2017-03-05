#!/usr/bin/python
# -*- coding: utf-8 -*-
from scrctrl.buffer import Buffer, FileContents
from scrctrl.window import Window, Position
from scrctrl.tab import Tab

import vim

from itertools import chain


def checkActiveElem(func):
    """
    もしVimオブジェクトが把握していないウィンドウおよびバッファがあればそのオブジェクトを作成して追加する
    """

    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
        except IndexError:
            evim = self if isinstance(self, Vim) else self._vim
            windows = evim._windows
            for winElem in vim.windows:
                if winElem not in windows:
                    evim.newWindow(winElem)
            buffers = evim._buffers
            for bufElem in vim.buffers:
                if bufElem not in buffers:
                    evim.newBuffer(bufElem)
            tabs = evim._tabs
            for tabElem in vim.tabpages:
                if tabElem not in tabs:
                    evim.newTab(tabElem)
            result = func(self, *args, **kwargs)
        return result
    return wrapper


def checkDeadElem(func):
    def wrapper(self, *args, **kwargs):
        evim = self if isinstance(self, Vim) else self._vim
        for win in evim._windows:
            if not win.isExist():
                evim.remove(evim)
        for buf in evim._buffers:
            if not buf.isOpen():
                evim.remove(buf)
        for tab in evim._tabs:
            if not tab.isExist():
                evim.remove(tab)

        return func(self, *args, **kwargs)
    return wrapper


class Vim(object):

    def __init__(self):
        self._buffers = []
        self._windows = []
        self._tabs = []

    def _initBuffer(self):
        for buf in vim.buffers:
            self.newBuffer(buf)

    def newBuffer(self, elem):
        return Buffer(elem, self)

    def _initWindow(self):
        for win in vim.windows:
            self.newWindow(win)

    def newWindow(self, elem):
        return Window(elem, self)

    def _initTab(self):
        for tab in vim.tabpages:
            self.newTab(tab)

    def newTab(self, elem):
        return Tab(elem, self)

    def getGlobalVar(self, varName, defaultIfNotFound=None):
        if defaultIfNotFound is None:
            return vim.vars.get(varName)
        return vim.vars.get(varName, defaultIfNotFound)

    def setGlobalVar(self, varName, value):
        vim.vars[varName] = value

    def getVimVar(self, varName, defaultIfNotFound=None):
        if defaultIfNotFound is None:
            return vim.vvars.get(varName)
        return vim.vvars.get(varName, defaultIfNotFound)

    def bufferFromIndex(self, index):
        return self._buffers[index]

    def bufferFromNumber(self, number):
        bufferElem = vim.buffers[number]
        return self.find(bufferElem)

    def window(self, index):
        return self._windows[index]

    @property
    def currentWindow(self):
        return self.find(vim.current.window)

    @checkActiveElem
    def find(self, elem):
        if isinstance(elem, vim.Window):
            return filter(lambda e: e.elem == elem, self._windows)[0]
        if isinstance(elem, vim.Buffer):
            return filter(lambda e: e.elem == elem, self._buffers)[0]
        if isinstance(elem, vim.TabPage):
            return filter(lambda e: e.elem == elem, self._tabs)[0]
        return None

    @checkDeadElem
    def findByTag(self, tag):
        for obj in chain.from_iterable([self._buffers, self._windows, self._tabs]):
            tagOfObj = obj.getTag()
            if tagOfObj == tag:
                return obj

    @checkDeadElem
    def findBufferByName(self, name):
        """
        拡張子抜きで比較して探す
        return Nullable
        """
        from os.path import splitext
        for buf in self._buffers:
            if buf.name == name or splitext(buf.name)[0] == name:
                return buf
        # else:
        #     raise ValueError('not found buffer by name ' + name)

    def remove(self, obj):
        try:
            if isinstance(obj, Window):
                self._windows.remove(obj)
            elif isinstance(obj, Buffer):
                self._buffers.remove(obj)
            elif isinstance(obj, Tab):
                self._tabs.remove(obj)
        except ValueError:
            # すでに取り除かれているオブジェクトを削除しようとした場合
            pass

    def appendBuffer(self, buffer):
        self._buffers.append(buffer)

    def appendWindow(self, window):
        self._windows.append(window)

    def appendTab(self, tab):
        self._tabs.append(tab)

    def __hash__(self):
        result = 17
        for buf in self._buffers:
            result = 31 * result + hash(buf.elem)
        for win in self._windows:
            result = 31 * result + hash(win.elem)
        for tab in self._tabs:
            result = 31 * result + hash(tab.elem)
        return result

    @staticmethod
    def toVimScriptValue(value):
        ret = value
        if isinstance(value, str):
            ret = '"' + value + '"'
        vim.command('let s:ret = ' + ret)


if __name__ == '__main__':
    print __package__
    vimObject = Vim()
    # vibjldjec.windw(aa2).getBuffer().setModifiable(True)
    # djkfa;sjfda;
    # djkfa;sjfda;
    # djkfa;sjfda;
    # djkfa;sjfda;
    # vjldfjlOi  t.  wiaaajljldndobbbw(2).getBuffer().setModifiable(True)

    # jkjfdlda;

    # aendTlle

    newBuffer = Window.builder(vimObject).pos(Position.LEFTEST).size(50).modifiable(False).moveActiveWindow(False).mapQStop(True).name('set name window').build().getBuffer()
    newBuffer.setTextContens(FileContents('/home/black-ubuntu/.vim/mapping.vim'))
