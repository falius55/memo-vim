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
        """
        return Nullable
        """
        currentBuffer = self.getCurrentBuffer()
        if currentBuffer.isMemoBuffer():
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

    # FIXME: ディレクトリの異なる同名ファイル(拡張子が違っても)を開いていたら適切なターゲットを取得できない
    def _findTargetBufferFrom(self, memoBuffer):
        """
        メモバッファーを渡すことでそのメモが対象としているテキストバッファを得られます
        return Nullable
        """
        vimObject = self._vim
        targetName = self.getTargetName(memoBuffer)
        if targetName is None:
            return None
        ret = vimObject.findBufferByName(targetName)
        return ret

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
