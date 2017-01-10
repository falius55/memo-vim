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
        vim.appendWindow(self)
        self._window = window
        self._vim = vim
        self._tag = {}

    def getBuffer(self):
        ret = self._vim.find(self._window.buffer)
        if ret is None:
            raise ValueError('this window has no buffer')
        return ret

    def getCursorPos(self):
        return self._window.cursor

    def setCursorPos(self, row, column):
        """
        カーソル移動イベントが発生します
        """
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

    def setOption(self, optionName, value):
        self._window.options[optionName] = value

    def getOption(self, optionName):
        return self._window.options[optionName]

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
        このウィンドウにカーソルを移動します
        この移動でautocmdは発火しません
        このウィンドウがすでになければ削除処理のみ行って見た目には何もしない
        """
        try:
            number = self.getNumber()
            vim.command('noautocmd %d wincmd w' % number)  # noautocmdをつけないと、関数の一連の処理の途中でmove()を使った場合にイベント処理が容赦なく割り込んできて想定外の動きとなってしまうことが多い
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
        self.move()
        vim.command('buffer %d' % self.getNumber())

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
    def builder(vim, bufClass=None, winClass=None):
        return WindowBuilder(vim, bufClass=bufClass, winClass=winClass)


class WindowBuilder(object):

    def __init__(self, vim, bufClass=None, winClass=None):
        if not issubclass(bufClass, Buffer):
            raise ValueError(str(bufClass) + ' is not subclass of Buffer')
        self._vim = vim
        self._pos = Position.LEFTEST
        self._size = 30
        self._modifiable = True
        self._moveActiveWindow = True
        self._mapQStop = False
        self._name = None
        self._bufType = None
        self._recycleBuffer = None
        self._filetype = None
        self._tag = None
        self._bufClass = bufClass
        self._winClass = winClass

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

    def fileType(self, filetype):
        self._filetype = filetype
        return self

    def tag(self, tag):
        """
        デフォルトのタグをつけます
        """
        self._tag = tag
        return self

    def build(self):
        saveWindow = self._vim.getCurrentWindow()

        newWindow = self._createWindow()
        newBuffer = newWindow.getBuffer()
        self._setSize(newWindow, self._size)
        newBuffer.setModifiable(self._modifiable)
        if self._name is not None:
            newBuffer.setName(self._name)
        if self._bufType is not None:
            newBuffer.setType(self._bufType)
        if self._filetype is not None:
            newBuffer.setFileType(self._filetype)
        if self._tag is not None:
            newBuffer.setTag(self._tag)

        self._setActiveWindow(self._moveActiveWindow, saveWindow)

        if self._mapQStop:
            newBuffer.mapQStop()
        return newWindow

    def _createWindow(self):
        if self._pos == Position.TOPPEST:
            vim.command('noautocmd topleft ' + self._argCommand(False, self._recycleBuffer))  # 画面分割でもcursorMovedイベントは発火してしまうため、noautocmdで抑制する
        elif self._pos == Position.LEFTEST:
            vim.command('noautocmd topleft ' + self._argCommand(True, self._recycleBuffer))
        elif self._pos == Position.RIGHTEST:
            vim.command('noautocmd botright ' + self._argCommand(True, self._recycleBuffer))
        elif self._pos == Position.DOWNEST:
            vim.command('noautocmd botright ' + self._argCommand(False, self._recycleBuffer))
        elif self._pos == Position.TOP:
            vim.command('noautocmd aboveleft ' + self._argCommand(False, self._recycleBuffer))
        elif self._pos == Position.LEFT:
            vim.command('noautocmd aboveleft ' + self._argCommand(True, self._recycleBuffer))
        elif self._pos == Position.RIGHT:
            vim.command('noautocmd belowright ' + self._argCommand(True, self._recycleBuffer))
        elif self._pos == Position.DOWN:
            vim.command('noautocmd belowright ' + self._argCommand(False, self._recycleBuffer))
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
        if self._bufClass:
            self._bufClass(newBufElem, self._vim)
        else:
            self._vim.newBuffer(newBufElem)

        newWinElem = self._findWindowElemFromBufferElem(newBufElem)
        if self._winClass:
            newWindow = self._winClass(newWinElem, self._vim)
        else:
            newWindow = self._vim.newWindow(newWinElem)
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
        elif Position.contains(self._pos, setableWidth):
            window.width(size)

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
