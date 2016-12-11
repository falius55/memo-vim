#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from constant import MEMO_BUFFER_TAG
from constant import ROW_TAG
from constant import BUFFER_TYPE
from constant import MEMO_SUMMARY


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
        if cursorPos is None:
            return
        print 'cursorPos', cursorPos
        memoBuffer.findWindow().setCursorPos(cursorPos, 0)



class MemoOpenState(object):

    @staticmethod
    def toMemoExistOnSameBuffer(memo, memoBuffer, row):
        memo.load(row, memoBuffer)

    @staticmethod
    def toMemoNotExistOnSameBuffer(memo, memoBuffer):
        # if memo.getBuffer():
            # TODO:ここでのif文は上のisMemoOpen()が誤った結果を返してしまう可能性によるもの。解決できれば外してもいい。このファイル内の他の箇所にある同部分に関しても同様
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
