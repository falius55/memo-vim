
function! memovim#mappings#set_memo_mappings() abort
    nmap <buffer> <C-t> <Plug>(toggle_summary_or_content)
    nmap <buffer> q <Plug>(leave_memo)
endfunction

function! memovim#mappings#set_summary_mappings() abort
    nmap <buffer> <CR> <Plug>(click_summary)
    nmap <buffer> i <Plug>(click_summary)
endfunction

function! memovim#mappings#unset_summary_mappings() abort
    try
        nunmap <buffer> <CR>
        nunmap <buffer> i
    catch  " まだマッピングされていないうちにummapされるとエラー。想定内なのでキャッチして続行する
    endtry
endfunction

function! memovim#mappings#set_content_mappings() abort
endfunction

function! memovim#mappings#unset_content_mappings() abort
endfunction
