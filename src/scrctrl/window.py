#!/usr/bin/python
# -*- coding: utf-8 -*-
from util.strenum import Enum
from util.utils import saveWindow
from scrctrl.buffer import Buffer
import vim

Position = Enum(
    'TOPPEST',
    'LEFTEST',
    'RIGHTEST',
    'DOWNEST',
    'TOP',
    'RIGHT',
    'LEFT',
    'DOWN'
)


def getPosition():
    return Position


class Window(object):
    DEFAULT_KEY = 'default_key'

    def __init__(self, window, vim):
        self._window = window
        self._vim = vim
        self._tag = {}

    def getBuffer(self):
        return self._vim.find(self._window.buffer)

    def getCursorPos(self):
        return self._window.cursor

    def setCursorPos(self, row, column):
        self._window.cursor = (row, column)

    def height(self, cntLine=None):
        if cntLine is None:
            return self._window.height
        self._window.height = cntLine

    def isExist(self):
        for winElem in vim.windows:
            if winElem == self._window:
                return True
        else:
            return False

    def width(self, cntColumn=None):
        if cntColumn is None:
            return self._window.width
        self._window.width = cntColumn

    def getVar(self, varName, defaultIfNotFound=None):
        """
        w: 変数
        """
        if defaultIfNotFound is None:
            return self._window.vars.get(varName)
        return self._window.vars.get(varName, defaultIfNotFound)

    def getNumber(self):
        """
        ウィンドウ番号。ウィンドウが削除されれば番号は詰められ、必ず各ウィンドウの番号は連番となる
        """
        return self._window.number

    def getPos(self):
        return (self._window.row, self._window.col)

    def setTag(self, key=None, tag=None):
        if key is None and tag is None:
            raise ValueError
        if key is None or tag is None:
            self._tag[Window.DEFAULT_KEY] = key if tag is None else tag
            return
        self._tag[key] = tag

    def getTag(self, key=None, defaultIfNotFound=None):
        if key is None:
            return self._tag.get(Window.DEFAULT_KEY, defaultIfNotFound)
        return self._tag.get(key, defaultIfNotFound)

    def elem(self):
        return self._window

    def move(self):
        """
        このウィンドウにカーソルを移動する
        このウィンドウがすでになければ削除処理のみ行って見た目には何もしない
        """
        try:
            number = self.getNumber()
            vim.command('%d wincmd w' % number)
        except vim.error:
            # すでに削除されたウィンドウにアクセスしようとした場合
            # 自身の参照を取り除いて続行する
            self._vim.remove(self)

    @saveWindow
    def printBuffer(self, buffer):
        """
        指定のバッファをこのウィンドウに表示する
        カーソルは動かない
        """
        # saveWindow = self._vim.getCurrentWindow()
        self.move()
        vim.command('buffer %d' % self.getNumber())
        # saveWindow.move()

    def __eq__(self, another):
        """
        vim標準との比較でも、同じウィンドウを指していればTrueを返す
        """
        if isinstance(another, Window):
            return self is another
        elif isinstance(another, vim.Window):
            return self._window is another
        return False

    def __hash__(self):
        """
        __eq__の仕様との関係上、vim標準のWindowオブジェクトと同一のハッシュ値を作成する
        """
        return hash(self._window)

    @staticmethod
    def builder(vim):
        return WindowBuilder(vim)


class WindowBuilder(object):

    def __init__(self, vim):
        self._vim = vim
        self._pos = Position.LEFTEST
        self._size = 30
        self._modifiable = True
        self._moveActiveWindow = True
        self._mapQStop = False
        self._name = None
        self._bufType = None
        self._recycleBuffer = None

    def pos(self, pos=Position.LEFTEST):
        if Position.stringFrom(pos) is None:
            raise ValueError()
        self._pos = pos
        return self

    def size(self, size=30):
        self._size = size
        return self

    def modifiable(self, modifiable):
        self._modifiable = modifiable
        return self

    def moveActiveWindow(self, move=True):
        self._moveActiveWindow = move
        return self

    def mapQStop(self, bl):
        self._mapQStop = bl
        return self

    def name(self, name):
        self._name = name
        return self

    def bufType(self, type):
        self._bufType = type
        return self

    def recycleBuffer(self, recycleBuffer):
        self._recycleBuffer = recycleBuffer
        return self

    def build(self):
        print 'window builder build()'
        saveWindow = self._vim.getCurrentWindow()

        newWindow = self._createWindow()
        newBuffer = newWindow.getBuffer()
        self._setSize(newWindow, self._size)
        newBuffer.setModifiable(self._modifiable)
        if self._name is not None:
            newBuffer.setName(self._name)
        if self._bufType is not None:
            newBuffer.setType(self._bufType)

        self._setActiveWindow(self._moveActiveWindow, saveWindow)

        if self._mapQStop:
            newBuffer.mapQStop()
        return newWindow

    def _createWindow(self):
        if self._pos == Position.TOPPEST:
            vim.command('topleft ' + self._argCommand(False, self._recycleBuffer))
        elif self._pos == Position.LEFTEST:
            vim.command('topleft ' + self._argCommand(True, self._recycleBuffer))
        elif self._pos == Position.RIGHTEST:
            vim.command('botright ' + self._argCommand(True, self._recycleBuffer))
        elif self._pos == Position.DOWNEST:
            vim.command('botright ' + self._argCommand(False, self._recycleBuffer))
        elif self._pos == Position.TOP:
            vim.command('aboveleft ' + self._argCommand(False, self._recycleBuffer))
        elif self._pos == Position.LEFT:
            vim.command('aboveleft ' + self._argCommand(True, self._recycleBuffer))
        elif self._pos == Position.RIGHT:
            vim.command('belowright ' + self._argCommand(True, self._recycleBuffer))
        elif self._pos == Position.DOWN:
            vim.command('belowright ' + self._argCommand(False, self._recycleBuffer))
        newWindow = self._keepUpVim()
        return newWindow

    def _argCommand(self, isVertical=False, recycleBuffer=None):
        if recycleBuffer is None:
            if isVertical:
                return 'vnew'
            else:
                return 'new'
        else:
            if isVertical:
                return 'vsp ' + recycleBuffer.getName()
            else:
                return 'sp ' + recycleBuffer.getName()

    def _keepUpVim(self):
        """
        VimオブジェクトにWindowとBufferを追加する
        """
        newBufElem = self._findLatestBufferElem()
        print 'keepup with memo buffer creating'
        newBuffer = Buffer(newBufElem, self._vim)
        self._vim.appendBuffer(newBuffer)

        newWinElem = self._findWindowElemFromBufferElem(newBufElem)
        newWindow = Window(newWinElem, self._vim)
        self._vim.appendWindow(newWindow)
        return newWindow

    def _findLatestBufferElem(self):
        bufferElem = reduce(lambda x, y: y if x.number < y.number else x,
                            vim.buffers)
        return bufferElem

    def _findWindowElemFromBufferElem(self, bufElem):
        for win in vim.windows:
            if win.buffer == bufElem:
                return win

    def _setSize(self, window, size):
        setableHeight = Position.TOPPEST | Position.DOWNEST | Position.TOP | Position.DOWN
        setableWidth = Position.LEFTEST | Position.RIGHTEST | Position.LEFT | Position.RIGHT

        if Position.contains(self._pos, setableHeight):
            window.height(size)
            print 'height setable'
        elif Position.contains(self._pos, setableWidth):
            window.width(size)
            print 'width setable'

    def _setActiveWindow(self, move, saveWindow):
        if move:
            pass
        else:
            saveWindow.move()


if __name__ == '__main__':
    print Position.names()
    print __package__
    print __name__
    from scrctrl.extendvim import Vim
    newWindow = WindowBuilder(Vim()).modifiable(False).pos(Position.TOPPEST).size(10).build()
    # newWindow.getBuffer().printing()
    # print 'modifiable ', newWindow.getBuffer().isModified()
    print 'buffer attr : ', newWindow.getBuffer().isModifiable()
