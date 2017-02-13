#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from constant import VAR_MEMO_OPEN

import vim


class StateManager(object):
    """
    設定も含めた現在の状況を管理するクラス
    """

    def __init__(self, bufferManager):
        self._bufferManager = bufferManager
        self._isSummary = False  # 目次を開く設定になっているかどうか

    def currentTargetLineNumber(self):
        """
        何行目にカーソルがあるか
        カーソル位置は１から始まる
        """
        targetBuffer = self._bufferManager.target
        return targetBuffer.findWindow().cursorPos[0]

    def lineNumberOfSummary(self):
        import re
        memoBuffer = self._bufferManager.memoBuffer
        lineNum = memoBuffer.findWindow().cursorPos[0]
        summaryLine = memoBuffer.getText(lineNum - 1)
        p = re.compile(r'^\[(\d+)\]\s*--\s.*$')
        match = p.match(summaryLine)
        if match:
            targetLine = match.group(1)
            return int(targetLine)

    def hasMemoOfCurrentLine(self):
        targetBuffer = self._bufferManager.target
        line = self.currentTargetLineNumber()
        return targetBuffer.memo.hasMemo(line)

    def isMemoOpened(self):
        memoBuffer = self._bufferManager.memoBuffer
        return memoBuffer is not None

    def isContentMemoOpened(self, row=None):
        if not self.isMemoOpened():
            return False
        memoBuffer = self._bufferManager.memoBuffer
        if row is None:
            return memoBuffer.isContents()
        else:
            return memoBuffer.row == row

    def isSummaryMemoOpened(self):
        if not self.isMemoOpened():
            return False
        memoBuffer = self._bufferManager.memoBuffer
        return memoBuffer.isSummary()

    def isInTargetBuffer(self):
        currentBuffer = self._bufferManager.current
        return currentBuffer.isTextBuffer()

    def isInMemoBuffer(self):
        currentBuffer = self._bufferManager.current
        return currentBuffer.isMemoBuffer()

    def isSummary(self):
        return self._isSummary

    def toggleSummaryOrContent(self):
        if self._isSummary:
            self._isSummary = False
        else:
            self._isSummary = True

    def isAlltimeMemoWindow(self):
        memoOpen = vim.vars.get(VAR_MEMO_OPEN, 0)

        if memoOpen == 2:
            return True
        return False

    def isRequiredMemoWindow(self):
        memoOpen = vim.vars.get(VAR_MEMO_OPEN, 0)
        if memoOpen == 1:
            return True
        return False

    def isInvalid(self):
        memoOpen = vim.vars.get(VAR_MEMO_OPEN, 0)
        if memoOpen == 0:
            return True
        return False

    def toAlltime(self):
        vim.vars[VAR_MEMO_OPEN] = 2

    def toInvalid(self):
        vim.vars[VAR_MEMO_OPEN] = 0

    def openConf(self):
        return vim.vars.get(VAR_MEMO_OPEN)
