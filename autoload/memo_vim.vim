" init.vimで利用する関数を定義する

function! memo_vim#open_window() abort
python << OPENMEMO
openMemoWindow()
OPENMEMO
endfunction

function! memo_vim#leave_memo() abort
python << LEAVEMEMO
leaveMemo()
LEAVEMEMO
endfunction

function! memo_vim#update_memo_position() abort
python << UPDATEPOSITION
updateMemoPosition()
UPDATEPOSITION
endfunction

function! memo_vim#delete_buffer() abort
python << DELETEBUFFER
deleteBuffer()
DELETEBUFFER
endfunction

function! memo_vim#moved_cursor() abort
python << MOVEDCURSOR
movedCursor()
MOVEDCURSOR
endfunction

function! memo_vim#write_to_file(bl) abort
python << SAVEFILE
writeMemoFile(int(vim.eval('a:bl')) != 0)
SAVEFILE
endfunction

function! memo_vim#delete_memo(...) abort
python << DELETEMEMO
deleteMemo(int(vim.eval('a:1')) if int(vim.eval('a:0')) > 0 else None)
DELETEMEMO
endfunction

function! memo_vim#move_memo(row, ...) abort
python << MOVEMEMO
if int(vim.eval('a:0')) == 1:
    fromRow = int(vim.eval('a:row'))
    toRow = int(vim.eval('a:1'))
    moveMemo(fromRow, toRow)
else:
    toRow = int(vim.eval('a:row'))
    moveMemo(None, toRow)
MOVEMEMO
endfunction

function! memo_vim#debug_memo() abort
python << MEMODEBUG
debugMemo()
MEMODEBUG
endfunction

function! memo_vim#toggle_memo() abort
python << TOGGLEMEMO
toggleMemo()
TOGGLEMEMO
endfunction

function! memo_vim#toggle_summary() abort
python << TOGGLESUMMARY
toggleIsSummary()
TOGGLESUMMARY
endfunction

function! memo_vim#tab_leave() abort
python << TABLEAVED
tabLeaved()
TABLEAVED
endfunction

function! memo_vim#memo_close() abort
python << MEMOCLOSE
closeMemo()
MEMOCLOSE
endfunction

function! memo_vim#next_memo() abort
python << NEXTMEMO
nextMemo()
NEXTMEMO
endfunction
function! memo_vim#prev_memo() abort
python << PREVMEMO
prevMemo()
PREVMEMO
endfunction
