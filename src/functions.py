#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from scrctrl.extendvim import Vim
from scrctrl.window import Window, Position

from textdiff import DiffParser
from event import operateByState
from util.utils import makeMemoName

from constant import MEMORY_PRE_TEXT
from constant import MEMO_BUFFER_TAG

import vim


def openWindow(moveActive=True):
    """
    メモウィンドウを開く処理
    """
    # すでに開かれていた場合、メモウィンドウにカーソルを移すのみ
    memoBuffer = vimObject.findByTag(MEMO_BUFFER_TAG)
    if memoBuffer is not None:
        if memoBuffer.findWindow():
            memoBuffer.findWindow().move()
        else:
            vimObject.remove(memoBuffer)
        return

    window = vimObject.getCurrentWindow()
    row = window.getCursorPos()[0]
    buffer = window.getBuffer()

    memoName = makeMemoName(buffer, row)
    memoWindow = Window.builder(vimObject).pos(Position.TOPPEST).name(memoName).size(5).moveActiveWindow(moveActive).bufType('acwrite').build()
    memoBuffer = memoWindow.getBuffer()
    memoBuffer.setTag(MEMO_BUFFER_TAG)
    buffer.getMemo().load(row, memoBuffer)
    # buffer.getMemo().setBuffer(memoBuffer)


def leave():
    """
    ウィンドウを出る直前
    """
    currentWindow = vimObject.getCurrentWindow()
    currentBuffer = currentWindow.getBuffer()
    if currentBuffer.getTag() != MEMO_BUFFER_TAG:
        return

    """
    メモウィンドウを出る直前ならそのメモ内容が変更されていれば更新する
    """
    if currentBuffer.getTag() == MEMO_BUFFER_TAG:
        memoBuffer = currentBuffer
        targetBuffer = findTargetBufferFrom(memoBuffer)
        targetWindow = targetBuffer.findWindow()
        if memoBuffer.isModified():
            row = targetWindow.getCursorPos()[0]
            memo = targetBuffer.getMemo()
            memo.keepOut(row, memoBuffer)
            memoBuffer.setModified(False)
        memoBuffer.finish()


def writeFile(bl):
    """
    ウィンドウを移動した時、編集ファイルが保存された時に、メモ内容もファイルに保存する
    """
    print 'write file'
    currentBuffer = vimObject.getCurrentWindow().getBuffer()
    if currentBuffer.getTag() == MEMO_BUFFER_TAG:
        memoBuffer = currentBuffer
        targetBuffer = findTargetBufferFrom(memoBuffer)
    else:
        targetBuffer = currentBuffer

    if bl:
        targetBuffer.findWindow().move()
        vim.command('w')
        targetBuffer.setModified(False)

    memo = targetBuffer.getMemo()

    # Memoオブジェクトに変更を通知する
    if memo.getBuffer():
        memoBuffer = memo.getBuffer()
        targetWindow = targetBuffer.findWindow()
        row = targetWindow.getCursorPos()[0]
        memo.keepOut(row, memoBuffer)
        memoBuffer.setModified(False)

    if memo.isEmpty():
        return

    memo.saveFile()


def updateMemoPosition():
    """
    対象バッファのテキストが変更された時など、メモの位置情報を更新する
    """
    currentBuffer = vimObject.getCurrentWindow().getBuffer()
    memo = currentBuffer.getMemo()

    if currentBuffer.getTag() == MEMO_BUFFER_TAG:
        return

    currentTextList = currentBuffer.getContentsList()
    preTextList = currentBuffer.getTag(key=MEMORY_PRE_TEXT, defaultIfNotFound=currentTextList)

    DiffParser(preTextList, currentTextList).start(
        addRowFunc=memo.notifyAddRow, deleteRowFunc=memo.notifyDeleteRow)

    currentBuffer.setTag(key=MEMORY_PRE_TEXT, tag=currentTextList)


def deleteBuffer():
    """
    バッファを削除した時、バッファオブジェクトの参照を取り除く
    """
    buffer = vimObject.getCurrentWindow().getBuffer()
    vimObject.remove(buffer)


def movedCursor():
    """
    カーソルが移動した時、状況によってメモウィンドウを開く、変更する、閉じるなどの動作を行います
    """
    operateByState(vimObject, openWindow)


def deleteMemo(row=None):
    currentBuffer = vimObject.getCurrentWindow().getBuffer()
    if currentBuffer.getTag() == MEMO_BUFFER_TAG:
        targetBuffer = findTargetBufferFrom(currentBuffer)
        memo = targetBuffer.getMemo()
        memo.getBuffer().finish()
        memo.setBuffer(None)
    else:
        targetBuffer = currentBuffer
        memo = targetBuffer.getMemo()

    if row is None:
        row = targetBuffer.findWindow().getCursorPos()[0]
    print 'delete memo', row
    if memo.hasMemo(row):
        print 'memo has'
        memo.deleteMemo(row)
        targetBuffer.findWindow().move()


def moveMemo(fromRow=None, toRow=None):
    """
    特定の行に紐付けられたメモを、別の行に移動します
    fromRowにNoneを渡した場合には、メモウィンドウ内で実行された場合にはそのメモの対象となる行が、通常のテキストバッファで実行された場合には現在いる行が対象となりtoRowに移動します
    また、移動先にすでにメモがあった場合は追記します
    """
    currentBuffer = vimObject.getCurrentWindow().getBuffer()
    if currentBuffer.getTag() == MEMO_BUFFER_TAG:
        targetBuffer = findTargetBufferFrom(currentBuffer)
        memo = targetBuffer.getMemo()
        memo.getBuffer().finish()
        memo.setBuffer(None)
    else:
        targetBuffer = currentBuffer
        memo = targetBuffer.getMemo()

    if fromRow is None:
        fromRow = targetBuffer.findWindow().getCursorPos()[0]

    memo.moveMemo(fromRow, toRow)
    targetBuffer.findWindow().move()


def initBuffer():
    """
    バッファが読み込まれた時点でのテキスト内容を保存する
    最初のバッファのコンストラクタは下記のグローバルスコープにおけるVim()内にて実行される。つまり、vimの設定ファイル内でpyfileを使って読み込まれる際に実行されるので、その時点ではバッファにテキストが読み込まれておらず空文字が取得されてしまう。そのため、バッファが読み込まれた際のイベントで内容を記憶する必要がある
    """
    buffer = vimObject.getCurrentWindow().getBuffer()
    buffer.setTag(key=MEMORY_PRE_TEXT, tag=buffer.getContentsList())


def findTargetBufferFrom(memoBuffer):
    """
    メモバッファーを渡すことでそのメモが対象としているテキストバッファを得られます
    """
    import re
    p = re.compile(r'[^-]+-([^-]+)-memo.*')
    match = p.match(memoBuffer.getName())
    if match:
        targetname = match.group(1)
        return vimObject.findBufferByName(targetname)
    raise TypeError('not found target from memo buffer')


def debug():
    try:
        print 'Buffer() list', [e.getName() for e in vimObject._buffers]
    except vim.error:
        print 'vim.error'
    print 'buffer elems', [e.name for e in vim.buffers]


if __name__ == '__main__':
    vimObject = globals().get('vimObject', Vim())
    preWindow = None
