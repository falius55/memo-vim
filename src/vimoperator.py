#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import vim

from buffermanager import BufferManager
from state import StateManager
from opener import Opener

from textdiff import DiffParser

from constant import MEMORY_PRE_TEXT


class Operator(object):

    def __init__(self, vim):
        self._vim = vim
        self._bufferManager = BufferManager(vim)
        self._state = StateManager(self._bufferManager)
        self._opener = Opener(vim, self._bufferManager, self._state)
        # self._cursorListener = CursorListener(self._stateManager, self._opener)

    def open(self):
        row = self._state.currentTargetLineNumber()
        self._opener.openContent(row)

    def movedCursor(self):
        if self._state.isInMemoBuffer():
            return
        self._opener.auto()

    def writeFile(self, bl):
        targetBuffer = self._bufferManager.getCurrentTargetBuffer()
        if targetBuffer is None:
            print '保存対象のファイルが見つかりません'
            return
        if bl:
            targetBuffer.findWindow().move()
            vim.command('w')
            targetBuffer.setModified(False)

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
        self._state.toggleSummaryOrContent()
        self._opener.auto()

    def initBuffer(self):
        if self._state.isInMemoBuffer():
            return
        targetBuffer = self._bufferManager.getCurrentBuffer()
        targetBuffer.setTag(MEMORY_PRE_TEXT, targetBuffer.getContentsList())


print 'readed operator'
if __name__ == '__main__':
    print 'readed'
