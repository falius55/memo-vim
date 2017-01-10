" メモウィンドウ内のマッピング
" メモウィンドウの状態は現状では２パターン
" すべての状態、概要状態、コンテンツ状態でそれぞれ有効無効の関数を定義する
" memobuffer.pyで使用

function! memovim#mappings#set_memo_mappings() abort
    nmap <buffer> <C-t> <Plug>(toggle_summary_or_content)
    nmap <buffer> q <Plug>(leave_memo)
endfunction

function! memovim#mappings#set_summary_mappings() abort
    nmap <buffer> <CR> <Plug>(click_summary)
    nmap <buffer> i <Plug>(click_summary)
    nmap <buffer> <C-l> <Plug>(click_summary)
endfunction

function! memovim#mappings#unset_summary_mappings() abort
    try
        nunmap <buffer> <CR>
        nunmap <buffer> i
        nunmap <buffer> <C-l>
    catch  " まだマッピングされていないうちにummapされるとエラー。想定内なのでキャッチして続行する
    endtry
endfunction

function! memovim#mappings#set_content_mappings() abort
    nmap <buffer> <ESC> <Plug>(open_summary)
    nmap <buffer> <C-h> <Plug>(open_summary)
endfunction

function! memovim#mappings#unset_content_mappings() abort
    try
        nunmap <buffer> <ESC>
        nunmap <buffer> <C-h>
    catch
    endtry
endfunction
