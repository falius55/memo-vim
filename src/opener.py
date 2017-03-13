#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from scrctrl.window import Window, Position
from scrctrl.memowindow import MemoWindow
from scrctrl.memobuffer import MemoBuffer

import vim


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
        isInMemo = self._state.isInMemoBuffer()  # もし処理途中でウィンドウを閉じてしまっても大丈夫なように、メモウィンドウ内にカーソルがある場合は覚えておく

        if self._state.isAlltimeMemoWindow():
            self._autoOnAlltime()
        elif self._state.isRequiredMemoWindow():
            self._autoOnRequired()
        elif self._state.isInvalid() and self._state.isMemoOpened():
            self.close()
            return

        if isInMemo:
            self._bufferManager.memoBuffer.findWindow().move()

    def openContent(self, row, moveActive=True):
        if not isinstance(row, int):
            raise ValueError('row is needed int type')
        targetBuffer = self._bufferManager.target
        if targetBuffer is None:
            return
        memo = targetBuffer.memo
        memoBuffer = self._openWindow()

        if self._state.isContentMemoOpened(row):
            pass
        else:
            memoBuffer.loadContent(memo, row)

        if moveActive:
            memoBuffer.findWindow().move()

    def openSummary(self, moveActive=True):
        """
        概要を開き、ターゲットバッファの現在行からもっとも近い位置にあるメモの概要にカーソルを当てます
        """
        targetBuffer = self._bufferManager.target
        memoBuffer = self._openWindow()
        memo = targetBuffer.memo

        memoBuffer.loadSummary(memo)

        if moveActive:
            memoBuffer.findWindow().move()

        lineNumber = self._state.currentTargetLineNumber()
        cursorPos = memo.indexOfKey(memo.closestRow(lineNumber)) + 1
        if cursorPos == 0:
            return
        memoBuffer.findWindow().cursorPos = (cursorPos, 0)

    def close(self):
        if self._state.isMemoOpened():
            memoBuffer = self._bufferManager.memoBuffer
            memoBuffer.finish()

            targetBuffer = self._bufferManager.target
            if targetBuffer is None:
                return
            memo = targetBuffer.memo
            memo.buffer = None

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
        # TODO: 働きをBufferManagerに移動
        memoBuffer = self._bufferManager.memoBuffer
        if memoBuffer is None:
            vim.command('normal =')
            memoWindow = Window.builder(self._vim, bufClass=MemoBuffer, winClass=MemoWindow).pos(Position.TOPPEST).moveActiveWindow(False).size(5).fileType('memovim').bufType('acwrite').build()
            memoWindow.setOption('winfixheight', True)
            memoBuffer = memoWindow.buffer

        return memoBuffer
