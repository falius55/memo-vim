#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import vim

from buffermanager import BufferManager
from state import StateManager
from opener import Opener
from util.utils import boundMode

from textdiff import DiffParser

from constant import MEMORY_PRE_TEXT
# from constant import MEMO_OPEN


class Operator(object):
    """
    操作を管理するクラス
    基本的にvim上のコマンドやオートコマンドに対応するメソッドを持つ
    """

    def __init__(self, vim):
        self._vim = vim
        self._bufferManager = BufferManager(vim)
        self._state = StateManager(self._bufferManager)
        self._opener = Opener(vim, self._bufferManager, self._state)

    def openContent(self):
        row = self._state.currentTargetLineNumber()
        self._opener.openContent(row)

    def openSummary(self):
        self._opener.openSummary(False)

    def leave(self):
        if self._state.isInTargetBuffer():
            return
        targetBuffer = self._bufferManager.getCurrentTargetBuffer()
        targetBuffer.findWindow().move()
        self.writeFile()

    @boundMode('n')  # ビジュアルモードでは、バッファのマッピング定義のためウィンドウ移動する際にビジュアルモードが解除されてしまうのでノーマルモードに限定する
    def movedCursor(self):
        if self._state.isInMemoBuffer():
            return
        self._opener.auto()

    def writeFile(self, bl=False):
        """
        bl : 本文テキストの書き込みを行うかどうか
        """
        targetBuffer = self._bufferManager.getCurrentTargetBuffer()
        if targetBuffer is None:
            print '保存対象のファイルが見つかりません'
            return
        if bl and self._state.isInTargetBuffer():
            # targetBuffer.findWindow().move()
            vim.command('w')
            # targetBuffer.setModified(False)

        memo = targetBuffer.getMemo()

        if self._state.isContentMemoOpened():
            memoBuffer = self._bufferManager.getTopMemoBuffer()
            row = self._state.currentTargetLineNumber()
            memo.keepOut(row, memoBuffer)
            memoBuffer.setModified(False)

        if memo.isEmpty():
            return

        memo.saveFile()

    def updateMemoPosition(self):
        if self._state.isInMemoBuffer():
            return
        targetBuffer = self._bufferManager.getCurrentTargetBuffer()
        currentTextList = targetBuffer.getContentsList()
        preTextList = targetBuffer.getTag(key=MEMORY_PRE_TEXT, defaultIfNotFound=currentTextList)
        memo = targetBuffer.getMemo()

        DiffParser(preTextList, currentTextList).start(addRowFunc=memo.notifyAddRow, deleteRowFunc=memo.notifyDeleteRow)

        targetBuffer.setTag(MEMORY_PRE_TEXT, currentTextList)
        self._opener.auto()

    def deleteMemo(self, row=None):
        if row is None:
            row = self._state.currentTargetLineNumber()
        targetBuffer = self._bufferManager.getCurrentTargetBuffer()
        targetBuffer.getMemo().deleteMemo(row)
        self._opener.auto()

    def moveMemo(self, fromRow=None, toRow=None):
        if fromRow is None:
            fromRow = self._state.currentTargetLineNumber()
        self._bufferManager.getCurrentTargetBuffer().getMemo().moveMemo(fromRow, toRow)
        self._opener.auto()

    def toggleSummaryOrContent(self):
        self.writeFile(False)
        self._state.toggleSummaryOrContent()
        self._opener.auto()

    # def initBuffer(self):
    #     if self._state.isInMemoBuffer():
    #         return
    #     targetBuffer = self._bufferManager.getCurrentBuffer()
    #     targetBuffer.setTag(MEMORY_PRE_TEXT, targetBuffer.getContentsList())

    def tabLeaved(self):
        self._opener.close()

    def toggleMemo(self):
        """
        メモウィンドウの有効無効を切り替える。これは'常にウィンドウを開く'と'ウィンドウを全く開かない'のトグルなので、必要に応じて開く設定にはならない
        """
        if self._state.isInvalid():
            self._state.toAlltime()
        else:
            self._state.toInvalid()
        self._opener.auto()

    def open(self):
        self._opener.auto()

    def close(self):
        self._state.toInvalid()
        self._opener.close()

    def clickSummary(self):
        lineNum = self._state.lineNumberOfSummary()
        if lineNum:
            self._opener.openContent(lineNum, False)
        else:
            print 'コンテンツが見つかりません'

    def nextMemo(self):
        if self._state.isInMemoBuffer():
            return
        currentTargetBuffer = self._bufferManager.getCurrentTargetBuffer()
        currentTargetWindow = currentTargetBuffer.findWindow()
        currentRow = currentTargetWindow.getCursorPos()[0]
        memo = currentTargetBuffer.getMemo()

        nextRow = memo.nextRow(currentRow)
        if nextRow is None:
            nextRow = memo.nextRow(0)
            if nextRow is None:
                print 'メモが見つかりませんでした'
                return
            else:
                print '後方にメモが見つからなかったので最初に戻ります'

        currentTargetWindow.setCursorPos(nextRow, 0)

    def prevMemo(self):
        if self._state.isInMemoBuffer():
            return
        currentTargetBuffer = self._bufferManager.getCurrentTargetBuffer()
        currentTargetWindow = currentTargetBuffer.findWindow()
        currentRow = currentTargetWindow.getCursorPos()[0]
        memo = currentTargetBuffer.getMemo()

        prevRow = memo.prevRow(currentRow)
        if prevRow is None:
            prevRow = memo.prevRow(currentTargetBuffer.getRowLen() + 1)
            if prevRow is None:
                print 'メモが見つかりませんでした'
                return
            else:
                print '前方にメモが見つからなかったので最後に戻ります'

        currentTargetWindow.setCursorPos(prevRow, 0)


if __name__ == '__main__':
    print 'readed'
