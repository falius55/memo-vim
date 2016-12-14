#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from constant import ROW_TAG
from constant import MEMO_BUFFER_TAG
from scrctrl.window import Window, Position


class Opener(object):
    """
    メモウィンドウの開閉を行うクラス
    """

    def __init__(self, vim, bufferManager, stateManager):
        self._vim = vim
        self._bufferManager = bufferManager
        self._state = stateManager

    def auto(self):
        """
        設定や現在位置によって自動で開閉を決定する
        カーソル位置は動かない
        """
        cursorSave = self._state.isInMemoBuffer()

        if self._state.isAlltimeMemoWindow():
            self._autoOnAlltime()
        else:
            self._autoOnRequired()

        if cursorSave:
            self._bufferManager.getTopMemoBuffer().findWindow().move()

    def openContent(self, row, moveActive=True):
        print 'open content', row
        if not isinstance(row, int):
            raise ValueError('row is needed int type')
        targetBuffer = self._bufferManager.getCurrentTargetBuffer()
        memo = targetBuffer.getMemo()
        memoBuffer = self._openWindow()
        print 'row tag', memoBuffer.getTag(ROW_TAG)

        if self._state.isContentMemoOpened(row):
            pass
        else:
            memo.load(row, memoBuffer)

        if moveActive:
            memoBuffer.findWindow().move()

    def openSummary(self, moveActive=True):
        targetBuffer = self._bufferManager.getCurrentTargetBuffer()
        memoBuffer = self._openWindow()
        memo = targetBuffer.getMemo()

        memo.loadSummary(memoBuffer)

        if moveActive:
            memoBuffer.findWindow().move()

        lineNumber = self._state.currentTargetLineNumber()
        cursorPos = memo.indexOfKey(memo.closestRow(lineNumber)) + 1
        if cursorPos == 0:
            return
        memoBuffer.findWindow().setCursorPos(cursorPos, 0)

    def close(self):
        if self._state.isMemoOpened():
            memoBuffer = self._bufferManager.getTopMemoBuffer()
            targetBuffer = self._bufferManager.getCurrentTargetBuffer()
            memo = targetBuffer.getMemo()
            memoBuffer.finish()
            memo.setBuffer(None)

    def _autoOnRequired(self):
        if self._state.hasMemoOfCurrentLine():
            self.openContent()
        else:
            self.close()

    def _autoOnAlltime(self):
        if not self._state.isSummary() and self._state.hasMemoOfCurrentLine():
            row = self._state.currentTargetLineNumber()
            self.openContent(row, False)
        else:
            self.openSummary(False)

    def _openWindow(self):
        """
        メモウィンドウが開いた状態にして、そのバッファを返す
        すでにメモウィンドウが開いていれば単にバッファを返すのみとなる
        """
        memoBuffer = self._bufferManager.getTopMemoBuffer()
        if memoBuffer is None:
            print 'new create window'
            memoWindow = Window.builder(self._vim).pos(Position.TOPPEST).moveActiveWindow(False).size(5).fileType('memo_vim').bufType('acwrite').build()
            memoBuffer = memoWindow.getBuffer()
            memoBuffer.setTag(MEMO_BUFFER_TAG)
        return memoBuffer
