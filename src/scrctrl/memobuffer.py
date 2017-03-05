#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from scrctrl.buffer import Buffer
from constant import MEMO_BUFFER_TAG
from constant import MEMO_DIRECTORY_PATH
from constant import MEMO_SUMMARY
from constant import MEMO_CONTENTS
from constant import MEMORY_PRE_TEXT
from util.utils import makeMemoName
from util.utils import makeSummaryName
from util.utils import saveWindow
from memo import Memo

import vim


class TextBuffer(Buffer):

    def __init__(self, buf, vim):
        Buffer.__init__(self, buf, vim)
        self._memo = Memo(self, MEMO_DIRECTORY_PATH)
        self.setTag(MEMORY_PRE_TEXT, self.contentsList)

    @property
    def memo(self):
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
        self._initMappings()
        self._target = None

    @saveWindow
    def _initMappings(self):
        self.findWindow().move()
        vim.command('call memovim#mappings#set_memo_mappings()')

    def isMemoBuffer(self):
        return True

    def isTextBuffer(self):
        return False

    def isContents(self):
        return self._type == MEMO_CONTENTS

    def isSummary(self):
        return self._type == MEMO_SUMMARY

    @property
    def row(self):
        """
        現在表示しているメモがターゲットバッファーの何行目に対応するかを返す。
        概要を表示しているならNoneが返る
        """
        return self._row

    @property
    def target(self):
        return self._target

    def loadContent(self, memo, row):
        if not isinstance(row, int):
            raise ValueError('row is not int type')
        self.clearText()
        content = memo.content(row)
        self.appendText(content)
        if self.getText(0) == '':
            self.deleteText(0)  # 最初の空行は削除する

        self.modified = False
        memoName = makeMemoName(memo.target, row)
        self.name = memoName
        self._row = row
        self._type = MEMO_CONTENTS
        self.modifiable = True
        self.type = 'acwrite'
        self.setOption('swapfile', False)
        self.findWindow().setOption('number', True)
        self.clearUndo()
        memo.buffer = self
        self._target = memo.target

        self._initContentMappings()

    def loadSummary(self, memo):
        summary = memo.summary()
        self.clearText()
        self.appendText(summary)
        if self.getText(0) == '':
            self.deleteText(0)

        self.modified = False
        summaryName = makeSummaryName(memo.target)
        try:
            self.name = summaryName
        except vim.error:
            print 'すでにある名前', summaryName
        self._row = None
        self._type = MEMO_SUMMARY
        self.modifiable = False
        self.type = 'nofile'
        self.setOption('swapfile', False)
        self.findWindow().setOption('number', False)
        memo.buffer = self
        self._target = memo.target

        self._initSummaryMappings()

    @saveWindow
    def _initSummaryMappings(self):
        self.findWindow().move()
        vim.command('call memovim#mappings#unset_content_mappings()')
        vim.command('call memovim#mappings#set_summary_mappings()')

    @saveWindow
    def _initContentMappings(self):
        self.findWindow().move()
        vim.command('call memovim#mappings#unset_summary_mappings()')
        vim.command('call memovim#mappings#set_content_mappings()')
