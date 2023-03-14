" Get the basic defaults
source $VIMRUNTIME/defaults.vim

" Don't clutter working directories with automatic backups and restore files
set nobackup	" do not keep a backup file, use versions instead
set nobackup	" do not keep a backup file (restore to previous version)
set noundofile	" do not keep an undo file (undo changes after closing)

if &t_Co > 2 || has("gui_running")
  " Switch on highlighting the last used search pattern.
  set hlsearch
endif

" Put these in an autocmd group, so that we can delete them easily.
augroup vimrcEx
  au!

  " For all text files set 'textwidth' to 78 characters.
  autocmd FileType text setlocal textwidth=78
augroup END

" Enables filetype detection, turns on highlighting, indentation
filetype plugin indent on
syntax on

" Use vim-plug to manage plugins
call plug#begin()
  Plug 'junegunn/vim-easy-align'
  Plug 'junegunn/fzf'
  Plug 'junegunn/fzf.vim'
  Plug 'preservim/nerdtree', { 'on': 'NERDTreeToggle' }
  Plug 'sainnhe/sonokai'
call plug#end()

let g:sonokai_style = 'andromeda'
let g:sonokai_better_performance = 1

colorscheme sonokai
