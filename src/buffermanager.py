#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from constant import MEMO_BUFFER_TAG


class BufferManager(object):
    """
    バッファオブジェクトの取得をサポートするクラス
    """

    def __init__(self, vim):
        self._vim = vim

    def getCurrentBuffer(self):
        return self._vim.getCurrentWindow().getBuffer()

    def getTopMemoBuffer(self):
        return self._vim.findByTag(MEMO_BUFFER_TAG)

    def getCurrentTargetBuffer(self):
        currentBuffer = self.getCurrentBuffer()
        if currentBuffer.getTag() == MEMO_BUFFER_TAG:
            return self._findTargetBufferFrom(currentBuffer)
        return currentBuffer

    def equals(self, targetBuffer, memoBuffer):
        """
        2つのバッファが同じテキストに対するものかどうか
        """
        from os.path import basename
        targetBaseName = basename(targetBuffer.getName())[0]
        targetName = self.getTargetName(memoBuffer)
        if targetName is None:
            return False
        memoTargetName = basename(targetName)[0]
        return targetBaseName == memoTargetName

    def _findTargetBufferFrom(self, memoBuffer):
        """
        メモバッファーを渡すことでそのメモが対象としているテキストバッファを得られます
        """
        vimObject = self._vim
        targetName = self.getTargetName(memoBuffer)
        if targetName is None:
            return None
        ret = vimObject.findBufferByName(targetName)
        return ret
        # if ret is not None:
        #     return ret
        # raise TypeError('not found target from memo buffer')

    @staticmethod
    def getTargetName(memoBuffer):
        """
        拡張子がある場合とない場合があるので注意
        """
        import re
        p = re.compile(r'[^-]+-([^-]+)-memo.*|summary--(.*)$')  # 後者はMemo.loadSummaryで定義
        match = p.match(memoBuffer.getName())
        if match:
            return match.group(match.lastindex)
        # raise TypeError('not found target from memo buffer')
