#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from constant import MEMO_BUFFER_TAG


class BufferManager(object):
    """
    バッファオブジェクトの取得をサポートするクラス
    """

    def __init__(self, vim):
        self._vim = vim

    @property
    def current(self):
        return self._vim.currentWindow.buffer

    @property
    def memoBuffer(self):
        return self._vim.findByTag(MEMO_BUFFER_TAG)

    @property
    def target(self):
        """
        return Nullable
        """
        currentBuffer = self.current
        if currentBuffer.isMemoBuffer():
            return currentBuffer.target
        return currentBuffer

    def equals(self, targetBuffer, memoBuffer):
        """
        2つのバッファが同じテキストに対するものかどうか
        """
        from os.path import basename
        targetBaseName = basename(targetBuffer.name)[0]
        targetName = self.getTargetName(memoBuffer)
        if targetName is None:
            return False
        memoTargetName = basename(targetName)[0]
        return targetBaseName == memoTargetName
