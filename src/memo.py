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


"""
一つのファイルに対するメモをまとめて管理するクラスです
"""


class Memo(object):

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
        if memoBuffer != self.getBuffer():
            raise ValueError('difference memoBuffer')
        if memoBuffer.getTag(ROW_TAG) != row:
            row = memoBuffer.getTag(ROW_TAG)

        memo = []
        for line in memoBuffer.elem():
            print 'keep out', line
            memo.append(line)
        self._memo[row] = memo
        print self._memo, row

    def load(self, row, memoBuffer):
        """
        指定行のメモ内容をメモバッファに書き込みます
        登録されているメモ内容がなければ空文字を書き込みます
        """
        print 'load', row
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
        self.setBuffer(memoBuffer)

    def loadSummary(self, memoBuffer):
        memo = self._memo
        summary = list(memo.keys())
        summary.sort()
        summaryList = ['%d %s' % (row, memo.get(row, [])[0]) for row in summary]
        memoBuffer.clearText()
        memoBuffer.appendText(summaryList)
        if memoBuffer.getText(0) == '':
            memoBuffer.deleteText(0)

        memoBuffer.setModified(False)
        memoBuffer.setName('summary--%s' % self._targetBuffer.getName())
        memoBuffer.setTag(key=BUFFER_TYPE, tag=MEMO_SUMMARY)
        summaryName = makeSummaryName(self._targetBuffer)
        self.setBuffer(memoBuffer)

    def indexOfKey(self, key):
        summary = list(self._memo.keys())
        summary.sort()
        return summary.index(key)

    def closestRow(self, row):
        if self.isEmpty():
            return None
        keys = self._memo.keys()
        minList = [abs(key - row) for key in keys]
        ret = keys[minList.index(min(minList))]
        return ret


    def saveFile(self):
        print 'open', open
        jsonString = json.dumps(self._memo)
        with open(self._saveFilePath, 'w') as f:
            f.write(jsonString)
        print 'saved to', self._saveFilePath

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
                print 'new key', (key + 1)
            else:
                break

    def _readFile(self, saveFilePath):
        print 'saveFilePath in _readFile', saveFilePath
        if not path.exists(saveFilePath):
            print 'filepath no exist'
            return {}

        with open(saveFilePath, 'r') as f:
            jsonString = f.read()

        ret = {}
        readObject = json.loads(jsonString)
        for key in readObject:
            ret[int(key)] = readObject[key]  # jsonから読み込むとキーが文字列になっているので整数に変換
        print 'keys in _readFile', ret.keys()
        return ret

    def deleteFile(self):
        from os import remove  # os自体をimportするとopen()が使えなくなる？
        remove(self._saveFile)

    def hasMemo(self, row):
        return row in self._memo

    # TODO: メモを削除した時にメモバッファが表示されている状態ならば、表示されているテキストをクリアする
    def deleteMemo(self, row):
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
