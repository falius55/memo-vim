#!/usr/bin/python3.4
# -*- coding: utf-8 -*-


def saveWindow(func):
    """
    分割などカレントウィンドウを変化させる処理があっても、変化を抑制する
    """
    import functools

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        vim = self._vim
        saveWindow = vim.getCurrentWindow()
        func(self, *args, **kwargs)
        saveWindow.move()
    return wrapper


def makeMemoName(targetBuffer, row):
    from os.path import splitext
    return '%sfile-%s-memo[%d]' % (targetBuffer.getFileType(), splitext(targetBuffer.getName())[0], row)
