#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from scrctrl.buffer import Buffer
from constant import MEMO_BUFFER_TAG
from constant import MEMO_DIRECTORY_PATH
from constant import MEMO_SUMMARY
from constant import MEMO_CONTENTS
from constant import ROW_TAG
from util.utils import makeMemoName
from util.utils import makeSummaryName
from memo import Memo

class TextBuffer(Buffer):

    def __init__(self, buf, vim):
        Buffer.__init__(self, buf, vim)
        self._memo = Memo(self, MEMO_DIRECTORY_PATH)

    def getMemo(self):
        return self._memo

    def isMemoBuffer(self):
        return False

    def isTextBuffer(self):
        return True


class MemoBuffer(Buffer):

    def __init__(self, buf, vim):
        Buffer.__init__(self, buf, vim)
        self.setTag(MEMO_BUFFER_TAG)
        self._type = None
        self._row = None

    def isMemoBuffer(self):
        return True

    def isTargetBuffer(self):
        return False

    def isContents(self):
        return self._type == MEMO_CONTENTS

    def isSummary(self):
        return self._type == MEMO_SUMMARY

    def row(self):
        return self._row

    def loadContent(self, memo, row):
        if not isinstance(row, int):
            raise ValueError('row is not int type')
        self.clearText()
        content = memo.content(row)
        self.appendText(content)
        if self.getText(0) == '':
            self.deleteText(0)  # 最初の空行は削除する

        self.setModified(False)
        memoName = makeMemoName(memo.getTarget(), row)
        self.setName(memoName)
        self._row = row
        self._type = MEMO_CONTENTS
        self.setModifiable(True)
        self.setType('acwrite')
        self.setOption('swapfile', False)
        self.findWindow().setOption('number', True)
        self.clearUndo()
        memo.setBuffer(self)

    def loadSummary(self, memo):
        summary = memo.summary()
        self.clearText()
        self.appendText(summary)
        if self.getText(0) == '':
            self.deleteText(0)

        self.setModified(False)
        summaryName = makeSummaryName(memo.getTarget())
        try:
            self.setName(summaryName)
        except vim.error:
            print 'すでにある名前', summaryName
        self._row = None
        self._type = MEMO_SUMMARY
        self.setModifiable(False)
        self.setType('nofile')
        self.setOption('swapfile', False)
        self.findWindow().setOption('number', False)
        memo.setBuffer(self)
