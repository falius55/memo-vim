#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import vim


def saveWindow(func):
    """
    分割などカレントウィンドウを変化させる処理があっても、変化を抑制する
    """
    import functools

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        evim = self._vim
        saveWindow = evim.currentWindow
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
    return '%s.memo[%d]' % (splitext(str(targetBuffer))[0], row)


def makeSummaryName(targetBuffer):
    from os.path import splitext
    return '%s.memo-summary' % splitext(str(targetBuffer))[0]
