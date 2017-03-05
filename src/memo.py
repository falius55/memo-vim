#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from os import path
import json

import vim


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
            filename = path.splitext(targetBuffer.name)[0] + '.memo'
            self._saveFilePath = path.join(savePath, filename)
        else:
            filename = path.splitext(str(targetBuffer))[0] + '.memo'
            if savePath.endswith('/'):
                savePath = savePath[:-1]
            if filename.startswith('/'):
                filename = filename[1:]
            self._saveFilePath = '/'.join([savePath, filename])
        self._memo = self._readFile(self._saveFilePath)

        self._targetBuffer = targetBuffer
        self._memoBuffer = None

    @property
    def buffer(self):
        return self._memoBuffer

    @buffer.setter
    def buffer(self, memoBuffer):
        self._memoBuffer = memoBuffer

    @property
    def target(self):
        return self._targetBuffer

    def isEmpty(self):
        return len(self._memo) == 0

    def isOpen(self):
        memoBuffer = self._memoBuffer
        if memoBuffer is None:
            return False
        try:
            if memoBuffer.elem in vim.buffer:
                return True
        except vim.error:  # すでに閉じられていれば例外が投げられるはず
            return False

    def keepOut(self, row, memoBuffer):
        """
        memoの内容をメモバッファから自身に取り込みます
        """
        if not memoBuffer.isContents():
            raise ValueError('not contents buffer is not kepon out')
        if memoBuffer != self.buffer:
            raise ValueError('difference memoBuffer')
        if memoBuffer.row != row:
            row = memoBuffer.row
        if memoBuffer.isEmpty():
            self.deleteMemo(row)
            return

        memo = []
        for line in memoBuffer.elem:
            memo.append(line)
        self._memo[row] = memo

    def content(self, row):
        return self._memo.get(row, [])

    def summary(self):
        if self.isEmpty():
            return ['empty']
        memo = self._memo
        keys = list(memo.keys())
        keys.sort()
        summary = [('[%d]' % row).ljust(6, ' ') + ' -- %s' % memo.get(row, [])[0] for row in keys]
        return summary

    def indexOfKey(self, key):
        summary = list(self._memo.keys())
        summary.sort()
        if key in summary:
            return summary.index(key)
        return -1

    def closestRow(self, row):
        """
        メモが存在する行のうち、指定行に最も近い行の数値を返す
        """
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
        import os
        if path.exists(self._saveFilePath):
            os.chmod(self._saveFilePath, 0o666)  # 読み書き可
        elif not path.exists(path.dirname(self._saveFilePath)):
            os.makedirs(path.dirname(self._saveFilePath))

        jsonString = json.dumps(self._memo)
        with open(self._saveFilePath, 'w') as f:
            f.write(jsonString)
            os.chmod(self._saveFilePath, 0o444)  # 読み込み専用

    def notifyDeleteRow(self, row):
        """
        本文のテキストに行が削除された時の処理
        削除行以降のメモの行を一行減らす
        """
        memo = self._memo
        for key in memo.keys():  # 削除や追加をループ内で行うため、キーリストをコピーしておくよう明示的にkeys()
            if key > row:
                if key - 1 in memo:
                    memo[key - 1].extend(memo[key])
                else:
                    memo[key - 1] = memo[key]
                del memo[key]

    def notifyAddRow(self, row):
        """
        行が追加された時の処理
        追加行以降の行を一行増やす
        """
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
        """
        JSON文字列のキーが数字でなければ無視する
        """
        if not path.exists(saveFilePath):
            return {}

        jsonString = ''
        with open(saveFilePath, 'r') as f:
            for line in f:
                jsonString += line

        ret = {}
        try:
            readObject = json.loads(jsonString)
        except json.JSONDecodeError:
            return {}
        # jsonから読み込むとキーが文字列になっているので整数に変換
        for key in readObject:
            if not key.isdigit():
                continue
            ret[int(key)] = readObject[key]
        return ret

    def deleteFile(self):
        from os import remove  # os自体をimportするとopen()が使えなくなる？
        remove(self._saveFile)

    def hasMemo(self, row):
        return row in self._memo

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
