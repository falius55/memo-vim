#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import vim

MEMORY_PRE_TEXT = 'memory_pre_text'  # テキストの差分を確認するために保持する、現在と同じ、あるいはテキストが変更された直後なら一つ前のテキスト状態を表す文字列のリスト

MEMO_BUFFER_TAG = 'memo_tag'  # メモバッファとそれ以外のバッファを区別するタグ

ROW_TAG = 'row'  # loadするときに表示するメモが対象としている行番号をタグとしてメモバッファーに取り付ける

BUFFER_TYPE = 'buffer_type'
MEMO_CONTENTS = 'memo_contents'
MEMO_SUMMARY = 'memo_summary'

# メモの保管先ディレクトリパス
try:
    MEMO_DIRECTORY_PATH = vim.eval('g:memo_vim_directorypath')
except vim.error:
    MEMO_DIRECTORY_PATH = None  # 変数が定義されていない

# ウィンドウの設定変数名
VAR_MEMO_OPEN = 'memo_open'

PLUGIN_DIR_PATH = vim.vars.get('dirpath')
