#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import vim

def saveWindow(func):
    """
    分割などカレントウィンドウを変化させる処理があっても、変化を抑制する
    """
    # TODO: ビジュアルモードでウィンドウ移動があった場合、ビジュアルモードが解除されてしまう
    import functools

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        vim = self._vim
        saveWindow = vim.getCurrentWindow()
        func(self, *args, **kwargs)
        saveWindow.move()
    return wrapper


def boundMode(mode):
    """
    関数が動作するモードを限定します
    'n' : ノーマルモード
    'c' : コマンドライン
    'v', 'V', 'CTRL-V' など : ビジュアルモード
    その他引数の詳細は:help mode()にて確認してください(vimのhelp)
    """
    def _boundMode(func):
        def wrapper(self, *args, **kwargs):
            cmode = vim.eval('mode()')
            if not cmode == mode:
                return
            ret = func(self, *args, **kwargs)
            return ret
        return wrapper
    return _boundMode


def makeMemoName(targetBuffer, row):
    from os.path import splitext
    return '%sfile-%s-memo[%d]' % (targetBuffer.getFileType(), splitext(targetBuffer.getName())[0], row)


def makeSummaryName(targetBuffer):
    from os.path import splitext
    return '%sfile-%s-memo-summary' % (targetBuffer.getFileType(), splitext(targetBuffer.getName())[0])
