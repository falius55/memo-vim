#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from os import path
import json

import vim

from constant import ROW_TAG


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
        memoName = 'memo %d %s' % (row, self._targetBuffer.getName())
        memoBuffer.setName(memoName)
        memoBuffer.setTag(key=ROW_TAG, tag=row)
        self.setBuffer(memoBuffer)

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
