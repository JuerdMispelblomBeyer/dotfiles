export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH
export ZSH="$HOME/.oh-my-zsh"


#-------------------------------------------------------------------------
# Oh My Zsh
#-------------------------------------------------------------------------
ZSH_THEME="afowler"
# CASE_SENSITIVE="true" # Case-sensitive completion.
# HYPHEN_INSENSITIVE="true" # Hyphen-insensitive completion. Case-sensitive completion must be off. _ and - will be interchangeable.
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time
# zstyle ':omz:update' frequency 13 # How often to auto-update (in days).
# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Core plugins (keep this list lean; heavy plugins load last below)
plugins=(
  git
  zsh-autosuggestions
  zsh-syntax-highlighting
)

# Autosuggestions sources for zsh-autosuggestions
ZSH_AUTOSUGGEST_STRATEGY=(history completion)

# Optional OMZ behaviors (uncomment as needed)
# CASE_SENSITIVE="true"
# HYPHEN_INSENSITIVE="true"
# zstyle ':omz:update' mode disabled
# ZSH_DISABLE_COMPFIX=true
# DISABLE_UNTRACKED_FILES_DIRTY="true"
# HIST_STAMPS="yyyy-mm-dd"
# ZSH_CUSTOM=/path/to/custom

ZSH_SRC="$ZSH/oh-my-zsh.sh"
[ -f "$ZSH_SRC" ] && source "$ZSH_SRC" || echo "\$ZSH/oh-my-zsh.sh not found at '$ZSH_SRC'"

#-------------------------------------------------------------------------
# Prompt (vcs_info)
#-------------------------------------------------------------------------
autoload -Uz vcs_info

# Show git branch and state markers
zstyle ':vcs_info:git:*' check-for-changes true
zstyle ':vcs_info:git:*' unstagedstr '*'
zstyle ':vcs_info:git:*' stagedstr '+'

# Format: ‹branch*+› (with action format identical)
zstyle ':vcs_info:git:*' formats $'\u2039%b%u\u203a '
zstyle ':vcs_info:git:*' actionformats $'\u2039%b%u\u203a '

# Refresh VCS info before each prompt
precmd() { vcs_info }

setopt PROMPT_SUBST
PROMPT='%F{#686de0}%n%f %F{blue}%B::%b %~%f %F{yellow}${vcs_info_msg_0_}%f%F{blue}»%f '


#-------------------------------------------------------------------------
# User config (optional examples)
#-------------------------------------------------------------------------
# export MANPATH="/usr/local/man:$MANPATH"
# export LANG=en_US.UTF-8
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='nvim'
# fi
# export ARCHFLAGS="-arch $(uname -m)"

#-------------------------------------------------------------------------
# Aliases
#-------------------------------------------------------------------------
# Open config files
alias zshconfig="xdg-open ~/.zshrc"

# Project shortcuts
alias dev="cd ~/Development"
alias exr="cd ~/Development/exr2"
alias core="cd ~/Development/exr2/exr2_core"
alias base="cd ~/Development/exr2/exr2_base"
alias operation="cd ~/Development/exr2/exr2_operation"
alias comms="cd ~/Development/exr2/exr2_communications"
alias sim="cd ~/Development/exr2/exr2_simulation"

# Safer defaults
alias mv="mv -iv"
alias cp="cp -riv"
alias mkdir="mkdir -vp "
alias rr="rm -r"

# Git shortcuts
alias gc="git clone"
alias gs="git status"
alias gb="git branch -r"
alias gp="git push"

# Docker shortcuts
alias dcl="docker container ls"
alias dcla="docker container ls -a"
alias dil="docker image ls"
alias dsp="docker system prune"
alias dnl="docker network ls"
alias dvl="docker volume ls"

#-------------------------------------------------------------------------
# Dotfiles loader
#-------------------------------------------------------------------------
export DOTFILES_DIR="$HOME/dotfiles"

# Load helper scripts (shell-agnostic)
[ -d "$DOTFILES_DIR" ] && . "$DOTFILES_DIR/shell/loader.sh"

#-------------------------------------------------------------------------
# History
#-------------------------------------------------------------------------
HISTSIZE=10000
SAVEHIST=10000

# Keep history across sessions and reduce noise
setopt append_history
setopt extended_history
setopt hist_expire_dups_first
setopt hist_ignore_dups
setopt hist_ignore_space
setopt hist_verify
setopt inc_append_history
setopt share_history

# Ignore trivial commands in history
zshaddhistory() {
  local cmd="${1%%$'\n'*}"  # Strip trailing newline
  local first="${cmd%% *}"
  case "$first" in
    ll|ls|la|clear|cd|man) return 1 ;;
  esac
  return 0
}

#-------------------------------------------------------------------------
# ROS 2
#-------------------------------------------------------------------------
# `ros` is provided by shell/loader.sh and lazy-loads ROS 2 env + aliases.

# Logging format
export RCUTILS_CONSOLE_OUTPUT_FORMAT="[{severity} {time}] [{name}]: {message} ({function_name}() at {file_name}:{line_number})"
export RCUTILS_COLORIZED_OUTPUT=1
# export RCUTILS_LOGGING_USE_STDOUT=1
# export RCUTILS_LOGGING_BUFFERED_STREAM=1

#-------------------------------------------------------------------------
# Plugins that must load last
#-------------------------------------------------------------------------
source ~/.oh-my-zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
source ~/.oh-my-zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
