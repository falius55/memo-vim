#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from os import path
import json

import vim

from constant import ROW_TAG
from constant import BUFFER_TYPE
from constant import MEMO_SUMMARY
from constant import MEMO_CONTENTS
from util.utils import makeMemoName
from util.utils import makeSummaryName


class Memo(object):
    """
    一つのファイルに対するメモをまとめて管理するクラスです
    """

    def __init__(self, targetBuffer, savePath=None):
        """
        savePathを指定しなければ対象のテキストファイルと同じディレクトリにメモファイルが作られる
        そのため、一箇所にまとめるにはパスを与える必要がある
        """
        if savePath is None:
            savePath = path.dirname(str(targetBuffer))
        self._saveFilePath = path.join(
            savePath,
            path.splitext(targetBuffer.getName())[0] + '-memo')
        self._memo = self._readFile(self._saveFilePath)

        self._targetBuffer = targetBuffer
        self._memoBuffer = None

    def setBuffer(self, memoBuffer):
        """
        自身の内容を表示するメモバッファを保持させる
        メモバッファが作成された時に設定し、
        メモバッファを破棄するときにNoneを設定する
        """
        self._memoBuffer = memoBuffer

    def getBuffer(self):
        return self._memoBuffer

    def isEmpty(self):
        return len(self._memo) == 0

    def isOpen(self):
        memoBuffer = self._memoBuffer
        if memoBuffer is None:
            return False
        try:
            if memoBuffer.elem() in vim.buffer:
                return True
        except vim.error:  # すでに閉じられていれば例外が投げられるはず
            return False

    def keepOut(self, row, memoBuffer):
        """
        memoの内容をメモバッファから自身に取り込みます
        """
        if memoBuffer.getTag(BUFFER_TYPE) != MEMO_CONTENTS:
            raise ValueError('not contents buffer is not kepon out')
        if memoBuffer != self.getBuffer():
            raise ValueError('difference memoBuffer')
        if memoBuffer.getTag(ROW_TAG) != row:
            row = memoBuffer.getTag(ROW_TAG)
        if memoBuffer.isEmpty():
            self.deleteMemo(row)
            return

        memo = []
        for line in memoBuffer.elem():
            memo.append(line)
        self._memo[row] = memo

    def load(self, row, memoBuffer):
        """
        指定行のメモ内容をメモバッファに書き込みます
        登録されているメモ内容がなければ空文字を書き込みます
        """
        if not isinstance(row, int):
            raise ValueError('row is not int type')
        memoBuffer.clearText()
        memo = self._memo.get(row, [])
        memoBuffer.appendText(memo)
        if memoBuffer.getText(0) == '':
            memoBuffer.deleteText(0)  # 最初の空行は削除する

        memoBuffer.setModified(False)
        memoName = makeMemoName(self._targetBuffer, row)
        memoBuffer.setName(memoName)
        memoBuffer.setTag(key=ROW_TAG, tag=row)
        memoBuffer.setTag(key=BUFFER_TYPE, tag=MEMO_CONTENTS)
        memoBuffer.setModifiable(True)
        memoBuffer.setType('acwrite')
        memoBuffer.setOption('swapfile', False)
        memoBuffer.findWindow().setOption('number', True)
        memoBuffer.clearUndo()
        self.setBuffer(memoBuffer)

    def loadSummary(self, memoBuffer):
        memo = self._memo
        summary = list(memo.keys())
        summary.sort()
        summaryList = [('[%d]' % row).ljust(6, ' ') + ' -- %s' % memo.get(row, [])[0] for row in summary]
        memoBuffer.clearText()
        memoBuffer.appendText(summaryList)
        if memoBuffer.getText(0) == '':
            memoBuffer.deleteText(0)

        memoBuffer.setModified(False)
        summaryName = makeSummaryName(self._targetBuffer)
        try:
            memoBuffer.setName(summaryName)
        except vim.error:
            print 'すでにある名前', summaryName
        memoBuffer.setTag(ROW_TAG, -1)
        memoBuffer.setTag(key=BUFFER_TYPE, tag=MEMO_SUMMARY)
        memoBuffer.setModifiable(False)
        memoBuffer.setType('nofile')
        memoBuffer.findWindow().setOption('number', False)
        self.setBuffer(memoBuffer)

    def indexOfKey(self, key):
        summary = list(self._memo.keys())
        summary.sort()
        if key in summary:
            return summary.index(key)
        return -1

    def closestRow(self, row):
        if self.isEmpty():
            return None
        keys = self._memo.keys()
        minList = [abs(key - row) for key in keys]
        ret = keys[minList.index(min(minList))]
        return ret

    def nextRow(self, row):
        """
        指定行より後にあるメモのうち、最初に見つかるメモが何行目にあるかを返します
        """
        if self.isEmpty():
            return None
        keys = self._memo.keys()
        keys.sort()
        for key in keys:
            if key > row:
                return key
        return None

    def prevRow(self, row):
        if self.isEmpty():
            return None
        keys = self._memo.keys()
        keys.sort(reverse=True)
        for key in keys:
            if key < row:
                return key
        return None

    def saveFile(self):
        jsonString = json.dumps(self._memo)
        with open(self._saveFilePath, 'w') as f:
            f.write(jsonString)

    def notifyDeleteRow(self, row):
        memo = self._memo
        if row in memo:
            del memo[row]
        for key in memo.keys():  # 削除や追加をループ内で行うため、キーリストをコピーしておくよう明示的にkeys()
            if key > row:
                content = memo[key]
                del memo[key]
                memo[key - 1] = content

    def notifyAddRow(self, row):
        if not isinstance(row, int):
            raise ValueError()
        memo = self._memo
        keys = sorted(memo.keys(), reverse=True)
        for key in keys:
            if key >= row:
                content = memo[key]
                del memo[key]
                memo[key + 1] = content
            else:
                break

    def _readFile(self, saveFilePath):
        if not path.exists(saveFilePath):
            return {}

        with open(saveFilePath, 'r') as f:
            jsonString = f.read()

        ret = {}
        readObject = json.loads(jsonString)
        for key in readObject:
            ret[int(key)] = readObject[key]  # jsonから読み込むとキーが文字列になっているので整数に変換
        return ret

    def deleteFile(self):
        from os import remove  # os自体をimportするとopen()が使えなくなる？
        remove(self._saveFile)

    def hasMemo(self, row):
        return row in self._memo

    # TODO: メモを削除した時にメモバッファが表示されている状態ならば、表示されているテキストをクリアする
    def deleteMemo(self, row):
        if self.hasMemo(row):
            del self._memo[row]

    def moveMemo(self, fromRow, toRow):
        if fromRow not in self._memo:
            return
        content = self._memo.get(fromRow, [])
        if toRow in self._memo:
            self._memo[toRow].extend(content)
        else:
            self._memo[toRow] = content
        del self._memo[fromRow]
