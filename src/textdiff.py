#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import difflib
import re


class DiffParser(object):

    def __init__(self, before, after, test=False):
        """
        beforeとafterはともに文字列のリスト
        """
        self._before = before
        self._after = after
        if test:
            self._test(before, after)

    def _test(self, before, after):
        """
        変更内容を正確に判断できるのは一手分の違いのみであることに注意(厳密には単純追加、単純削除以外で二行以上のずれが生じるとダメ)
        """
        self._beforeStart = None
        self._beforeRange = None
        self._afterStart = None
        self._afterRange = None
        result = difflib.unified_diff(before, after)
        minusList = set()
        plusList = set()
        self._result = result
        p = re.compile(r'@@.*[-+](\d+),(\d+).*[+-](\d+),(\d+).*@@')
        minusP = re.compile(r'^\s*-(?!--)')
        plusP = re.compile(r'^\s*[+](?![+][+])')
        beforeIndex = -1
        afterIndex = -1
        for i, line in enumerate(result):
            matches = p.match(line)
            minusMatches = minusP.match(line)
            plusMatches = plusP.match(line)
            if matches:
                self._beforeStart = int(matches.group(1))
                self._beforeRange = int(matches.group(2))
                self._afterStart = int(matches.group(3))
                self._afterRange = int(matches.group(4))
                beforeIndex = self._beforeStart
                afterIndex = self._afterStart
                print '%3d %15s %18s %s' % (i, ' title match:', ' ', line)
            elif minusMatches:
                print '%3d %15s %15s %s' % (i, ' minusMatches:', (beforeIndex, None), line)
                minusList.add(beforeIndex)
                beforeIndex = beforeIndex + 1
            elif plusMatches:
                print '%3d %15s %15s %s' % (i, ' plusMatches:', (None, afterIndex), line)
                plusList.add(afterIndex)
                afterIndex = afterIndex + 1
            elif i < 2:
                print '%3d %15s %15s %s' % (i, ' i < 3:', (None, None), line)
            else:
                print '%3d %15s %15s %s' % (i, ' else:', (beforeIndex, afterIndex), line)
                beforeIndex = beforeIndex + 1
                afterIndex = afterIndex + 1
        else:
            print 'result : ', ' '.join(map(str, (self._beforeStart, self._beforeRange, self._afterStart, self._afterRange)))
            print 'plus:', plusList
            print 'minus:', minusList
            print 'simple add:', plusList.difference(minusList)
            print 'simple remove:', minusList.difference(plusList)
            print 'changed row:', plusList.intersection(minusList)

    def start(self, addRowFunc=None, deleteRowFunc=None, changeRowFunc=None, closeFunc=None):
        """
        単純追加された行の行番号を一つ一つaddRowFuncに渡して実行し、
        同様にしてdeleteRowFuncとchangeRowFuncも実行します
        closeFuncは最後に一度だけ実行されます
        closeFuncを除いた関数が一度でも実行されればTrueを返します
        """
        result = self._analyze(self._before, self._after)
        ret = False

        if addRowFunc is not None:
            for rowNum in sorted(result[0]):
                addRowFunc(rowNum)
                ret = True
        if deleteRowFunc is not None:
            for rowNum in sorted(result[1]):
                deleteRowFunc(rowNum)
                ret = True
        if changeRowFunc is not None:
            for rowNum in sorted(result[2]):
                changeRowFunc(rowNum)
                ret = True
        if closeFunc is not None:
            closeFunc()

        return ret

    def _analyze(self, before, after):
        """
        戻り値はタブル
        1: 単純追加行のセット
        2: 単純削除行のセット
        3: 内容変更行のセット
        """
        result = difflib.unified_diff(before, after)

        titlePattern = re.compile(r'@@.*[-+](\d+),(\d+).*[+-](\d+),(\d+).*@@')
        minusPattern = re.compile(r'^\s*-(?!--)')
        plusPattern = re.compile(r'^\s*[+](?![+][+])')

        plusSet = set()
        minusSet = set()
        beforeIndex = -1
        afterIndex = -1
        for i, line in enumerate(result):
            titleMatches = titlePattern.match(line)
            minusMatches = minusPattern.match(line)
            plusMatches = plusPattern.match(line)
            if i < 2:
                pass
            elif titleMatches:
                beforeIndex = int(titleMatches.group(1))
                afterIndex = int(titleMatches.group(3))
            elif minusMatches:
                minusSet.add(beforeIndex)
                beforeIndex = beforeIndex + 1
            elif plusMatches:
                plusSet.add(afterIndex)
                afterIndex = afterIndex + 1
            else:
                beforeIndex = beforeIndex + 1
                afterIndex = afterIndex + 1
        simpleAdd = plusSet.difference(minusSet)
        simpleDelete = minusSet.difference(plusSet)
        change = plusSet.intersection(minusSet)
        return simpleAdd, simpleDelete, change
