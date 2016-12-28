#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from constant import MEMO_BUFFER_TAG
from constant import BUFFER_TYPE
from constant import MEMO_CONTENTS
from constant import MEMO_SUMMARY
from constant import ROW_TAG
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
        targetBuffer = self._bufferManager.getCurrentTargetBuffer()
        return targetBuffer.findWindow().getCursorPos()[0]

    def lineNumberOfSummary(self):
        import re
        memoBuffer = self._bufferManager.getTopMemoBuffer()
        lineNum = memoBuffer.findWindow().getCursorPos()[0]
        summaryLine = memoBuffer.getText(lineNum - 1)
        p = re.compile(r'^\[(\d+)\]\s*--\s.*$')
        match = p.match(summaryLine)
        if match:
            targetLine = match.group(1)
            return int(targetLine)

    def hasMemoOfCurrentLine(self):
        targetBuffer = self._bufferManager.getCurrentTargetBuffer()
        line = self.currentTargetLineNumber()
        return targetBuffer.getMemo().hasMemo(line)

    def isMemoOpened(self):
        memoBuffer = self._bufferManager.getTopMemoBuffer()
        return memoBuffer is not None

    def isContentMemoOpened(self, row=None):
        if not self.isMemoOpened():
            return False
        memoBuffer = self._bufferManager.getTopMemoBuffer()
        if row is None:
            return memoBuffer.isContents()
        else:
            return memoBuffer.row() == row

    def isSummaryMemoOpened(self):
        if not self.isMemoOpened():
            return False
        memoBuffer = self._bufferManager.getTopMemoBuffer()
        return memoBuffer.isSummary()

    def isInTargetBuffer(self):
        currentBuffer = self._bufferManager.getCurrentBuffer()
        return currentBuffer.isTextBuffer()

    def isInMemoBuffer(self):
        currentBuffer = self._bufferManager.getCurrentBuffer()
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
