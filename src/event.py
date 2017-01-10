#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from constant import MEMO_BUFFER_TAG
from constant import ROW_TAG
from constant import BUFFER_TYPE
from constant import MEMO_SUMMARY
from constant import MEMO_CONTENTS
from constant import MEMORY_PRE_TEXT

from scrctrl.window import Window, Position
from textdiff import DiffParser
import vim


def isMemoOpen(vim):
    memoBuffer = vim.findByTag(MEMO_BUFFER_TAG)
    return memoBuffer is not None and memoBuffer.findWindow() is not None


def isSameBuffer(vim):
    """
    メモが開かれていることを前提とした判断
    """
    memoBuffer = vim.findByTag(MEMO_BUFFER_TAG)
    memoName = memoBuffer.getName()
    currentBuffer = vim.getCurrentWindow().getBuffer()
    return currentBuffer.getName() in memoName


def isInMemoBuffer(vim):
    currentBuffer = vim.getCurrentWindow().getBuffer()
    return currentBuffer.getTag() == MEMO_BUFFER_TAG


def operateByState(vim, openWindow, isAlltimeOpenBuffer, isSummary):
    """
    isAlltimeOpenBuffer: メモウィンドウを常に表示する設定になっているかどうか
    isSummary: 概要を表示する設定になっているかどうか(そうでなければメモ内容を表示)
    """
    currentWindow = vim.getCurrentWindow()
    currentBuffer = currentWindow.getBuffer()
    lineNumber = currentWindow.getCursorPos()[0]
    memo = currentBuffer.getMemo()
    memoBuffer = vim.findByTag(MEMO_BUFFER_TAG)

    if isInMemoBuffer(vim):
        return

    if isAlltimeOpenBuffer:
        if memoBuffer is None:
            openWindow(False)
            memoBuffer = vim.findByTag(MEMO_BUFFER_TAG)
        alltimeOpen(isSummary, memo, memoBuffer, lineNumber)
        return

    if isMemoOpen(vim):
        if isSameBuffer(vim):
            if memoBuffer.getTag(ROW_TAG) == lineNumber:
                MemoOpenState.toSameRow()
                return
            if memo.hasMemo(lineNumber):
                MemoOpenState.toMemoExistOnSameBuffer(memo, memoBuffer, lineNumber)
            else:
                MemoOpenState.toMemoNotExistOnSameBuffer(memo, memoBuffer)
        else:
            if memo.hasMemo(lineNumber):
                MemoOpenState.toMemoExistOnDifferenceBuffer(memo, memoBuffer, openWindow)
            else:
                MemoOpenState.toMemoNotExistOnDifferenceBuffer(memo, memoBuffer)
    else:
        if memo.hasMemo(lineNumber):
            # NotMemoOpenState.toMemoExistOnSameBuffer()
            # NotMemoOpenState.toMemoExistOnDifferenceBuffer()
            # print 'globals in event.py', globals()
            openWindow(False)
        else:
            # NotMemoOpenState.toMemoNotExistOnSameBuffer()
            # NotMemoOpenState.toSameRow()
            # NotMemoOpenState.toMemoNotExistOnDifferenceBuffer()
            pass


def alltimeOpen(isSummary, memo, memoBuffer, row):
    if not isSummary and memo.hasMemo(row):
        memo.load(row, memoBuffer)
    else:
        if memoBuffer.getTag(key=BUFFER_TYPE) != MEMO_SUMMARY:
            memo.loadSummary(memoBuffer)
        # TODO: MemoのclosestRow(row)を使って、最も位置が近いメモ概要行にカーソルを当てる
        cursorPos = memo.indexOfKey(memo.closestRow(row)) + 1
        if cursorPos == 0:
            return
        print 'cursorPos', cursorPos
        memoBuffer.findWindow().setCursorPos(cursorPos, 0)


class MemoOpenState(object):

    @staticmethod
    def toMemoExistOnSameBuffer(memo, memoBuffer, row):
        memo.load(row, memoBuffer)

    @staticmethod
    def toMemoNotExistOnSameBuffer(memo, memoBuffer):
        memoBuffer.finish()
        memo.setBuffer(None)

    @staticmethod
    def toSameRow():
        pass

    @staticmethod
    def toMemoExistOnDifferenceBuffer(memo, memoBuffer, openWindow):
        # if memo.getBuffer():
        memoBuffer.finish()
        memo.setBuffer(None)
        '''
        　importしたものを使うと再読み込みが発生し、なおかつ__name__=='__main__'
        でないためvimObjectが定義されず、openWindow()内でエラーが発生する。
        　そのため関数を参照で受け取って実行する。
        　しかしエラーが発生したあとでコマンドからopenWindow()を実行しても
        エラーにはならず。
        importすると異なるモジュールスコープが発生し、そのスコープ由来の関数
        であるからエラーとなり、参照で受け取った関数はメインで実行されたモ
        ジュールスコープ由来だからvimObjectが定義されていたということか
        '''
        openWindow(False)

    @staticmethod
    def toMemoNotExistOnDifferenceBuffer(memo, memoBuffer):
        print 'メモあり --> メモなし　別バッファ'
        # if memo.getBuffer():
        memoBuffer.finish()
        memo.setBuffer(None)


class NotMemoOpenState(object):

    def toMemoExistOnSameBuffer(self):
        # openWindow(False)
        pass

    def toMemoNotExistOnSameBuffer(self):
        pass

    def toSameRow(self):
        pass

    def toMemoExistOnDifferenceBuffer(self):
        # openWindow(False)
        pass

    def toMemoNotExistOnDifferenceBuffer(self):
        pass


class InMemoState(object):

    def returnTargetBuffer(self):
        pass

    def toSameRow(self):
        pass

    def toDefferenceTargetBuffer(self):
        pass


class WindowState(object):

    def __init__(self, vim):
        self._vim = vim

    def open(self, moveActive=True):
        """
        メモウィンドウを開く処理(openコマンド)
        """
        vimObject = self._vim
        window = vimObject.getCurrentWindow()
        row = window.getCursorPos()[0]
        buffer = window.getBuffer()
        if buffer.getTag(BUFFER_TYPE) == MEMO_BUFFER_TAG:
            buffer = self.findTargetBufferFrom(buffer)
        Opener(vimObject, buffer).openContent(row, moveActive)

    def writeFile(self, bl):
        print 'write file'
        vimObject = self._vim
        currentBuffer = vimObject.getCurrentWindow().getBuffer()
        if currentBuffer.getTag() == MEMO_BUFFER_TAG:
            memoBuffer = currentBuffer
            targetBuffer = self.findTargetBufferFrom(memoBuffer)
        else:
            targetBuffer = currentBuffer

        if bl:
            targetBuffer.findWindow().move()
            vim.command('w')
            targetBuffer.setModified(False)

        memo = targetBuffer.getMemo()

        # Memoオブジェクトに変更を通知する
        if memo.getBuffer() and memo.getBuffer().getTag(key=BUFFER_TYPE) == MEMO_CONTENTS:
            memoBuffer = memo.getBuffer()
            targetWindow = targetBuffer.findWindow()
            row = targetWindow.getCursorPos()[0]
            memo.keepOut(row, memoBuffer)
            memoBuffer.setModified(False)

        if memo.isEmpty():
            return

        memo.saveFile()

    def updateMemoPosition(self):
        vimObject = self._vim
        currentBuffer = vimObject.getCurrentWindow().getBuffer()
        memo = currentBuffer.getMemo()

        if currentBuffer.getTag() == MEMO_BUFFER_TAG:
            return

        currentTextList = currentBuffer.getContentsList()
        preTextList = currentBuffer.getTag(key=MEMORY_PRE_TEXT, defaultIfNotFound=currentTextList)

        DiffParser(preTextList, currentTextList).start(
            addRowFunc=memo.notifyAddRow, deleteRowFunc=memo.notifyDeleteRow)

        currentBuffer.setTag(key=MEMORY_PRE_TEXT, tag=currentTextList)

    def deleteMemo(self, row=None):
        vimObject = self._vim
        currentBuffer = vimObject.getCurrentWindow().getBuffer()
        if currentBuffer.getTag() == MEMO_BUFFER_TAG:
            targetBuffer = self.findTargetBufferFrom(currentBuffer)
            memo = targetBuffer.getMemo()
            memo.getBuffer().finish()
            memo.setBuffer(None)
        else:
            targetBuffer = currentBuffer
            memo = targetBuffer.getMemo()

        if row is None:
            row = targetBuffer.findWindow().getCursorPos()[0]
        print 'delete memo', row
        if memo.hasMemo(row):
            print 'memo has'
            memo.deleteMemo(row)
            targetBuffer.findWindow().move()

    def moveMemo(self, fromRow=None, toRow=None):
        vimObject = self._vim
        currentBuffer = vimObject.getCurrentWindow().getBuffer()
        if currentBuffer.getTag() == MEMO_BUFFER_TAG:
            targetBuffer = self.findTargetBufferFrom(currentBuffer)
            memo = targetBuffer.getMemo()
            memo.getBuffer().finish()
            memo.setBuffer(None)
        else:
            targetBuffer = currentBuffer
            memo = targetBuffer.getMemo()

        if fromRow is None:
            fromRow = targetBuffer.findWindow().getCursorPos()[0]

        memo.moveMemo(fromRow, toRow)
        targetBuffer.findWindow().move()

    def movedCursor(self):
        if self._isInMemoBuffer():
            return

    def findTargetBufferFrom(self, memoBuffer):
        """
        メモバッファーを渡すことでそのメモが対象としているテキストバッファを得られます
        """
        vimObject = self._vim
        targetName = WindowState.getTargetName(memoBuffer)
        ret = vimObject.findBufferByName(targetName)
        if ret is not None:
            return ret
        raise TypeError('not found target from memo buffer')

    @staticmethod
    def getTargetName(memoBuffer):
        """
        拡張子のない名前を取得
        """
        import re
        p = re.compile(r'[^-]+-([^-]+)-memo.*|summary--(.*)$')  # 後者はMemo.loadSummaryで定義
        match = p.match(memoBuffer.getName())
        if match:
            return match.group(match.lastindex)
        raise TypeError('not found target from memo buffer')

    def _isInMemoBuffer(self):
        currentBuffer = self._vim.getCurrentWindow().getBuffer()
        return currentBuffer.getTag() == MEMO_BUFFER_TAG

    def hasMemoHere(self):
        pass

    def _isAlltimeOpenBuffer(self):
        try:
            memoOpen = int(vim.eval('g:memo_open'))
        except vim.error:
            memoOpen = 0

        if memoOpen == 0:
            return False
        elif memoOpen == 1:
            return True


class RequiredOpenState(WindowState):

    def movedCursor(self):
        pass


class AlltimeOpenState(WindowState):

    def movedCursor(self):
        pass


class Opener(object):

    def __init__(self, vim, targetBuffer):
        self._vim = vim
        self._targetBuffer = targetBuffer
        self._memo = targetBuffer.getMemo()

    def openContent(self, row, moveActive=True):
        memoBuffer = self._getMemoBuffer()
        if memoBuffer.getTag(BUFFER_TYPE) == MEMO_CONTENTS and memoBuffer.getTag(ROW_TAG, row):
            pass
        else:
            self._memo.load(row, memoBuffer)
        if moveActive:
            memoBuffer.findWindow().move()

    def openSummary(self, moveActive=True):
        memoBuffer = self._getMemoBuffer()
        if memoBuffer.getTag(BUFFER_TYPE) == MEMO_SUMMARY and self._vim.findByName(WindowState.getTargetName(memoBuffer)) == self._targetBuffer:
            pass
        else:
            self._memo.loadSummary(memoBuffer)
        if moveActive:
            memoBuffer.findWindow().move()

    def _getMemoBuffer(self):
        memoBuffer = self._vim.findByTag(MEMO_BUFFER_TAG)
        if memoBuffer is None:
            # メモバッファが閉じていれば、ウィンドウを作成する
            memoWindow = Window.builder(self._vim).pos(Position.TOPPEST).size(5).bufType('acwrite').build()
            memoBuffer = memoWindow.getBuffer()
            memoBuffer.setTag(MEMO_BUFFER_TAG)
        return memoBuffer
