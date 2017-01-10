#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from scrctrl.memovim import MemoVim
from vimoperator import Operator

import vim


def openMemoWindow(moveActive=True):
    """
    メモウィンドウを開く処理
    """
    operator.openContent()


def leaveMemo():
    operator.leave()


def closeMemo():
    operator.close()


def writeMemoFile(bl):
    """
    ウィンドウを移動した時、編集ファイルが保存された時に、メモ内容もファイルに保存する
    """
    operator.writeFile(bl)


def updateMemoPosition():
    """
    対象バッファのテキストが変更された時など、メモの位置情報を更新する
    """
    operator.updateMemoPosition()


def movedCursor():
    """
    カーソルが移動した時、状況によってメモウィンドウを開く、変更する、閉じるなどの動作を行います
    """
    operator.movedCursor()


def toggleIsSummary():
    operator.toggleSummaryOrContent()


def toggleMemo():
    operator.toggleMemo()


def deleteMemo(row=None):
    operator.deleteMemo(row)


def moveMemo(fromRow=None, toRow=None):
    """
    特定の行に紐付けられたメモを、別の行に移動します
    fromRowにNoneを渡した場合には、メモウィンドウ内で実行された場合にはそのメモの対象となる行が、通常のテキストバッファで実行された場合には現在いる行が対象となりtoRowに移動します
    また、移動先にすでにメモがあった場合は追記します
    """
    operator.moveMemo(fromRow, toRow)


# def initBuffer():
#     """
#     バッファが読み込まれた時点でのテキスト内容を保存する
#     最初のバッファのコンストラクタは下記のグローバルスコープにおけるVim()内にて実行される。つまり、vimの設定ファイル内でpyfileを使って読み込まれる際に実行されるので、その時点ではバッファにテキストが読み込まれておらず空文字が取得されてしまう。そのため、バッファが読み込まれた際のイベントで内容を記憶する必要がある
#     """
#     operator.initBuffer()


def tabLeaved():
    operator.tabLeaved()


def jumpSummary():
    operator.jumpSummary()


def clickSummary():
    operator.clickSummary()


def openSummary():
    operator.openSummary()


def nextMemo():
    operator.nextMemo()


def prevMemo():
    operator.prevMemo()


def debugMemo():
    try:
        print 'Buffer() list', [e.getName() for e in vimObject._buffers]
    except vim.error:
        print 'vim.error'
    print 'buffer elems', [e.name for e in vim.buffers]
    print 'buffer tags', [e.getTag() for e in vimObject._buffers]
    print 'buffer class', [e.__class__ for e in vimObject._buffers]


if __name__ == '__main__':
    vimObject = globals().get('vimObject', MemoVim())
    isSummary = False
    operator = globals().get('operator', Operator(vimObject))
