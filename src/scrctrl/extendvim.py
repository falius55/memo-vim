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
            wvim = self if isinstance(self, Vim) else self._vim
            windows = wvim._windows
            for winElem in vim.windows:
                if winElem not in windows:
                    wvim.appendWindow(Window(winElem, wvim))
            buffers = wvim._buffers
            for bufElem in vim.buffers:
                if bufElem not in buffers:
                    print 'checkElem decolator appendBuffer'
                    wvim.appendBuffer(Buffer(bufElem, wvim))
            result = func(self, *args, **kwargs)
        return result
    return wrapper


def checkDeadElem(func):
    def wrapper(self, *args, **kwargs):
        wvim = self if isinstance(self, Vim) else self._vim
        for win in wvim._windows:
            if not win.isExist():
                wvim.remove(wvim)
        for buf in wvim._buffers:
            if not buf.isExist():
                wvim.remove(buf)
        for tab in wvim._tabs:
            if not tab.isExist():
                wvim.remove(tab)

        return func(self, *args, **kwargs)
    return wrapper


class Vim(object):

    def __init__(self):
        print 'Vim() create'
        self._initBuffer()
        self._initWindow()
        self._initTab()

    def _initBuffer(self):
        buffers = []
        for buf in vim.buffers:
            buffers.append(Buffer(buf, self))
        self._buffers = buffers

    def _initWindow(self):
        windows = []
        for win in vim.windows:
            windows.append(Window(win, self))
        self._windows = windows

    def _initTab(self):
        tabs = []
        for tab in vim.tabpages:
            tabs.append(Tab(tab, self))
        self._tabs = tabs

    def getGlobalVar(self, varName, defaultIfNotFound=None):
        if defaultIfNotFound is None:
            return vim.vars(varName)
        return vim.vars(varName, defaultIfNotFound)

    def getVimVar(self, varName, defaultIfNotFound=None):
        if defaultIfNotFound is None:
            return vim.vvars(varName)
        return vim.vvars(varName, defaultIfNotFound)

    def bufferFromIndex(self, index):
        return self._buffers[index]

    def bufferFromNumber(self, number):
        bufferElem = vim.buffers[number]
        return self.find(bufferElem)

    def window(self, index):
        return self._windows[index]

    def getCurrentWindow(self):
        return self.find(vim.current.window)

    @checkActiveElem
    def find(self, elem):
        if isinstance(elem, vim.Window):
            return filter(lambda e: e.elem() == elem, self._windows)[0]
        if isinstance(elem, vim.Buffer):
            return filter(lambda e: e.elem() == elem, self._buffers)[0]
        if isinstance(elem, vim.TabPage):
            return filter(lambda e: e.elem() == elem, self._tabs)[0]
        return None

    @checkDeadElem
    def findByTag(self, tag):
        for obj in chain.from_iterable([self._buffers, self._windows, self._tabs]):
            tagOfObj = obj.getTag()
            if tagOfObj == tag:
                return obj

    @checkDeadElem
    def findBufferByName(self, name):
        from os.path import splitext
        for buf in self._buffers:
            if buf.getName() == name or splitext(buf.getName())[0] == name:
                return buf

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
        print 'append buffer'
        self._buffers.append(buffer)

    def appendWindow(self, window):
        print 'append window'
        self._windows.append(window)

    def __hash(self):
        result = 17
        for buf in self._buffers:
            result = 31 * result + hash(buf.elem())
        for win in self._windows:
            result = 31 * result + hash(win.elem())
        for tab in self._tabs:
            result = 31 * result + hash(tab.elem())
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
