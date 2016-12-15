#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
from scrctrl.extendvim import Vim
from scrctrl.memobuffer import TextBuffer

class MemoVim(Vim):

    def __init__(self):
        Vim.__init__(self)

    def newBuffer(self, elem):
        return TextBuffer(elem, self)

