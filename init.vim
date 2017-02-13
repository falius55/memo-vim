if (exists('b:did_memovim'))
    finish
endif
let b:did_memovim = 1

let b:not_read = 0
if b:not_read == 1
    finish
endif

let g:memo_vim_directorypath = $HOME.'/.memo'  " メモを保存するディレクトリ。このディレクトリに、'同等のディレクトリパス/対象ファイル名.memo'で保存される
let g:memo_open = 2  " メモウィンドウの設定 0:全く開かない 1: 必要に応じて開く 2: 常に開いた状態にしておく

let g:dirpath = fnamemodify(resolve(expand('<sfile>:p')), ':h')  " 現在ディレクトリ。関数内では書けない
function! s:init_py() abort
    if (exists('b:inited_memovim'))
        return
    endif
    let b:inited_memovim = 1

    let l:srcpath = g:dirpath."/src"
    let l:init_py_file = l:srcpath."/init.py"
    let l:function_py_file = l:srcpath."/functions.py"
    execute 'pyfile '.l:init_py_file
python << INITPYTHON
import vim
memovim_init_path(vim.eval('l:srcpath'))
INITPYTHON
    execute 'pyfile '.l:function_py_file
endfunction


comman! OpenMemo call memo_vim#open_window()

command! SaveMemo call memo_vim#write_to_file(0)

" メモウィンドウの開閉
command! ToggleMemoVim call memo_vim#toggle_memo()

command! ToggleSummary call memo_vim#toggle_summary()

command! -nargs=? DeleteMemo call memo_vim#delete_memo(<args>)

command! -nargs=+ MoveMemo call memo_vim#move_memo(<f-args>)

command! DebugMemo call memo_vim#debug_memo()

command! CloseMemo call memo_vim#memo_close()

command! StartMemo call s:startMemo()

command! StopMemo call s:stopMemo()

function! s:setAutoCommand() abort
    augroup memovim_autocmd
        autocmd!
        autocmd TextChanged * call memo_vim#update_memo_position()

        autocmd TextChangedI * call memo_vim#update_memo_position()

        autocmd CursorMoved,WinEnter * call memo_vim#moved_cursor()  " カーソルが移動した時、別のウィンドウに入った時

        autocmd WinLeave * call memo_vim#write_to_file(0)  " ウィンドウを移動した時

        autocmd BufWinLeave * call memo_vim#write_to_file(0)  " バッファが破棄された時

        autocmd TabLeave * call memo_vim#tab_leave()
    augroup END
endfunction

function! s:removeAutoCommand() abort
    autocmd! memovim_autocmd
endfunction

function! s:startMemo() abort
    if (exists('s:cach_memo_open'))
        let g:memo_open = s:cach_memo_open
    endif
    call s:init_py()
    call s:setAutoCommand()
endfunction

function! s:stopMemo() abort
    if !(exists('b:inited_memovim'))
        return
    endif
    if (exists('g:memo_open'))
        let s:cach_memo_open = g:memo_open
    endif
    CloseMemo
    call s:removeAutoCommand()
endfunction

call s:startMemo()

" プラグインの機能をマップ用に定義する
" <Plug>(click_summary)でマップできるようになる
" メモウィンドウ内で実行すると、対象テキストのあるバッファのカーソルが指定位置まで飛ぶ
" nnoremap <silent> <Plug>(jump_summary) :<C-u>call memo_vim#summary_jump()<CR>
" 次のメモのある位置までカーソルが飛ぶ
nnoremap <silent> <Plug>(next_memo) :<C-u>call memo_vim#next_memo()<CR>
nnoremap <silent> <Plug>(prev_memo) :<C-u>call memo_vim#prev_memo()<CR>
nnoremap <silent> <Plug>(toggle_summary_or_content) :<C-u>call memo_vim#toggle_summary()<CR>
nnoremap <silent> <Plug>(open_memo) :<C-u>call memo_vim#open_window()<CR>
nnoremap <silent> <Plug>(toggle_memo) :<C-u>call memo_vim#toggle_memo()<CR>
nnoremap <silent> <Plug>(leave_memo) :<C-u>call memo_vim#leave_memo()<CR>
nnoremap <silent> <Plug>(click_summary) :<C-u>python clickSummary()<CR>
nnoremap <silent> <Plug>(open_summary) :<C-u>python openSummary()<CR>

