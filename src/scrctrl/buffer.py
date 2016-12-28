#!/usr/bin/python
# -*- coding: utf-8 -*-
from memo import Memo
from util.utils import saveWindow
from constant import MEMO_DIRECTORY_PATH

import vim


def checkTextChange(func):
    """
    テキスト変更前後の処理をするデコレータ
    modifiableがオフならば、一時的にオンにする
    さらに、変更されても保存せずに閉じられるように変更通知を取り消す
    """

    def wrapper(self, *args, **kwargs):
        if self.isModifiable():
            result = func(self, *args, **kwargs)
            return result

        self.setModifiable(True)

        result = func(self, *args, **kwargs)

        self.setModifiable(False)
        self.setModified(False)  # modifiableがfalseなら、変更されても保存せずに閉じられるように変更通知を取り消す
        return result
    return wrapper


class Buffer(object):
    """
    バッファを表すクラスです。
    同じバッファが複数ウィンドウで表示されている場合でも、
    そのいずれも同じオブジェクトが担当しますので注意してください
    """
    DEFAULT_KEY = 'default_key'

    def __init__(self, buf, vim):
        vim.appendBuffer(self)
        self._buf = buf
        self._vim = vim
        self._tag = {}

    def __str__(self):
        """
        フルパス名
        """
        return self._buf.name

    def setName(self, name):
        """
        @throw vim.error すでに存在する名前をつけようとした場合
        """
        self._buf.name = name

    def getName(self):
        """
        パスで名はなく、単純なファイル名
        """
        from os.path import basename
        return basename(str(self))

    def setTag(self, key=None, tag=None):
        """
        このインスタンスにタグをつけます
        識別用の値以外でも汎用的に値をひもづけることができます
        keyとtagが両方渡されなかった場合はValueErrorを投げますが、
        片方のみNone以外の値が渡され、もう一方がNoneである場合にはデフォルトのキーでNoneでない値を保存します
        """
        if key is None and tag is None:
            raise ValueError
        if key is None or tag is None:
            self._tag[Buffer.DEFAULT_KEY] = key if tag is None else tag
            return
        self._tag[key] = tag

    def getTag(self, key=None, defaultIfNotFound=None):
        """
        あらかじめ紐付けられたタグを返します
        キーが渡されなかった場合には、デフォルトのキーに紐付いた値があればそれを返します
        """
        if key is None:
            return self._tag.get(Buffer.DEFAULT_KEY, defaultIfNotFound)
        return self._tag.get(key, defaultIfNotFound)

    def elem(self):
        return self._buf

    def getNumber(self):
        return self._buf.number

    def findWindow(self):
        """
        同じバッファが複数ウィンドウで表示されていて、かつそのいずれにも現在カーソルが
        ない場合には最初に見つかったウィンドウのオブジェクトを返します。
        もしそのいずれかに現在カーソルがある場合は、カーソルのあるウィンドウのオブジェクトを返します。
        """
        if self.isCurrent():
            return self._vim.find(vim.current.window)
        for win in vim.windows:
            if win.buffer == self._buf:
                return self._vim.find(win)
        return None

    def getOption(self, optionName):
        return self._buf.options[optionName]

    def getOptions(self):
        return self._buf.options

    def setOption(self, optionName, value):
        self._buf.options[optionName] = value

    def getVar(self, varName, defaultIfNotFound=None):
        """
        バッファ変数
        """
        if defaultIfNotFound is None:
            return self._buf.vars.get(varName)
        return self._buf.vars.get(varName, defaultIfNotFound)

    def isExist(self):
        """
        バッファリストに自身があるかどうか
        """
        for bufElem in vim.buffers:
            if bufElem == self._buf:
                return True
        else:
            return False

    def isOpen(self):
        return self.findWindow() is not None

    def isCurrent(self):
        return vim.current.buffer is self._buf

    @checkTextChange
    def appendText(self, strOrList, lineNum=None):
        if lineNum is None:
            self._buf.append(strOrList)
        else:
            self._buf.append(strOrList, lineNum)

    def getText(self, index):
        """
        テキストのインデックスは０から始まる
        """
        return self._buf[index]

    @checkTextChange
    def replaceText(self, index, string):
        self._buf[index] = string

    @checkTextChange
    def clearText(self):
        del self._buf[:]

    @checkTextChange
    def prependText(self, string):
        self._buf[0:0] = string

    @checkTextChange
    def deleteText(self, index):
        del self._buf[index]

    @checkTextChange
    def setTextContents(self, contents):
        """
        writeTextメソッドを実装したオブジェクトを渡してテキストをセットします
        """
        contents.writeText(self)

    def getRowLen(self):
        return len(self._buf)

    def isEmpty(self):
        if self.getRowLen() == 0:
            return True
        return self.getRowLen() == 1 and self.getText(0).lstrip() == ''

    def isModified(self):
        """
        テキストが変更されたのかどうか([＋]がついているかどうか)
        """
        return self._buf.options['modified']

    def setModified(self, isModified=True):
        self._buf.options['modified'] = isModified

    def setModifiable(self, canModifiable):
        """
        Falseを設定することで変更できなくなる
        @param canModifiable 真偽値
        """
        self._buf.options['modifiable'] = canModifiable

    def isModifiable(self):
        """
        修正可能かどうかの真偽値
        """
        return self._buf.options['modifiable']

    def setFileType(self, filetype):
        """
        filetypeは文字列だが、空白が含まれているとエラー
        """
        self._buf.options['filetype'] = filetype

    def getFileType(self):
        return self._buf.options['filetype']

    @saveWindow
    def mapQStop(self, canStop=True):
        """
        qを入力することでバッファが閉じるようにするかどうか
        """
        window = self.findWindow()
        window.move()
        if canStop:
            vim.command('nnoremap <buffer> q :<C-u>bd<CR>')
        else:
            vim.command('nunmap <buffer> q')

    def setType(self, type):
        self._buf.options['buftype'] = type

    def getContentsList(self):
        return [line for line in self._buf]

    def __eq__(self, another):
        """
        vim標準との比較でも、同じバッファを指していればTrueを返す
        """
        if isinstance(another, Buffer):
            return self is another
        elif isinstance(another, vim.Buffer):
            return self._buf is another
        return False

    def __hash__(self):
        return hash(self._buf)

    @saveWindow
    def finish(self):
        window = self.findWindow()
        if window is None:
            self._vim.remove(self)
            return

        window.move()
        vim.command('bd')
        self._vim.remove(window)
        self._vim.remove(self)

    @saveWindow
    def clearUndo(self):
        """
        undoスタックをクリアする
        """
        self.findWindow().move()
        vim.command('let old_undolevels = &undolevels')
        vim.command('set undolevels=-1')
        vim.command('exe "normal a \<BS>\<ESC>"')
        vim.command('let &undolevels = old_undolevels')
        vim.command('unlet old_undolevels')
        self.setModified(False)

    @saveWindow
    def source(self, path):
        self.findWindow().move()
        vim.command('source ' + path)


class FileContents(object):

    def __init__(self, filepath):
        self._filepath = filepath

    def writeText(self, buffer):
        with open(self._filepath) as f:
            buffer.appendText(list(f))


if __name__ == '__main__':
    print __package__
    from scrctrl.extendvim import Vim
    vimObject = globals().get('vimObject', Vim())
    curBuffer = vimObject.getCurrentWindow().getBuffer()
    if not hasattr(curBuffer, '_contents'):
        curBuffer.memoryContents()
        print 'memory current buffer:', curBuffer._buf.name
    else:
        curBuffer.isChanged()
