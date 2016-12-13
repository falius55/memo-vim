let b:not_read = 0
if b:not_read == 1
    finish
endif

let g:memo_vim_directorypath = '/home/black-ubuntu/.vim/plugin/memos'  " メモを保存するディレクトリ。このディレクトリに、'対象ファイル名-memo'で保存される
let g:memo_effect = 1  " カーソル移動イベントの有効無効 0:無効 1:有効
let g:memo_open = 1  " メモウィンドウを常に開くのか、必要に応じて開くのか 0: 必要に応じて開く 1: 常に開いた状態にしておく

let s:dirpath = fnamemodify(resolve(expand('<sfile>:p')), ':h')  " 関数内では書けない
function! s:init_py() abort
    let l:srcpath = s:dirpath."/src"
    let l:init_py_file = l:srcpath."/init.py"
    let l:function_py_file = l:srcpath."/functions.py"
    execute 'pyfile '.l:init_py_file
python << INITPYTHON
import vim
init_path(vim.eval('l:srcpath'))
INITPYTHON
    execute 'pyfile '.l:function_py_file
endfunction

call s:init_py()

comman! OpenMemo call memo_vim#open_window()

command! UpdatePositon call memo_vim#update_memo_position()

command! SaveMemo call memo_vim#write_to_file(0)

command! ToggleMemoVim call memo_vim#toggle_autcmd_group()

command! ToggleSummary call memo_vim#toggle_summary()

command! -nargs=? DeleteMemo call memo_vim#delete_memo(<args>)

command! -nargs=+ MoveMemo call memo_vim#move_memo(<f-args>)

command! DebugMemo call memo_vim#debug_memo()

autocmd! TextChanged * call memo_vim#update_memo_position()

autocmd! TextChangedI * call memo_vim#update_memo_position()

" autocmd! BufLeave * call memo_vim#leave_and_keepout()

autocmd! WinLeave * call memo_vim#write_to_file(0)  " ウィンドウを移動した時

autocmd! BufWriteCmd * call memo_vim#write_to_file(1)  " wによって書き込みされた時。acwriteでないバッファまでwrite_to_file以外で保存できなくなる？

autocmd! BufWinLeave * call memo_vim#write_to_file(0)  " バッファが破棄された時

autocmd! BufRead * call memo_vim#init_buffer()



call memo_vim#set_autcmd_group(g:memo_effect)
