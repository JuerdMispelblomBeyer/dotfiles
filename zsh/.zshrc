# If you come from bash you might have to change your $PATH.
export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH
export ZSH="$HOME/.oh-my-zsh"

#-------------------------------------------------------------------------
# Themes
#-------------------------------------------------------------------------
ZSH_THEME="afowler"

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
	git 
	zsh-autosuggestions
    zsh-syntax-highlighting
)

# Agressive autocompletion
ZSH_AUTOSUGGEST_STRATEGY=(history completion)

source $ZSH/oh-my-zsh.sh

#-------------------------------------------------------------------------
# Custom Prompt
# For VCS prompt settings: https://git-scm.com/book/ms/v2/Appendix-A:-Git-in-Other-Environments-Git-in-Zsh
#-------------------------------------------------------------------------
autoload -Uz vcs_info

zstyle ':vcs_info:git:*' check-for-changes true
zstyle ':vcs_info:git:*' unstagedstr '*'
zstyle ':vcs_info:git:*' stagedstr '+'

zstyle ':vcs_info:git:*' formats      $'\u2039%b%u\u203a '
zstyle ':vcs_info:git:*' actionformats $'\u2039%b%u\u203a '

precmd() { vcs_info }

setopt PROMPT_SUBST
PROMPT='%F{#686de0}%n%f %F{blue}%B::%b %~%f %F{yellow}${vcs_info_msg_0_}%f%F{blue}»%f '


#-------------------------------------------------------------------------
# User configuration
#-------------------------------------------------------------------------
# export MANPATH="/usr/local/man:$MANPATH"
# You may need to manually set your language environment
# export LANG=en_US.UTF-8
# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='nvim'
# fi
# Compilation flags
# export ARCHFLAGS="-arch $(uname -m)"



# Personal aliases
# overriding those provided by Oh My Zsh libs, plugins, and themes. Aliases can be placed here, though Oh My Zsh
# users are encouraged to define aliases within a top-level file in the $ZSH_CUSTOM folder, with .zsh extension. 
# For a full list of active aliases, run `alias`. Examples:
# - $ZSH_CUSTOM/aliases.zsh
# - $ZSH_CUSTOM/macos.zsh
# Example aliases
# alias ohmyzsh="mate ~/.oh-my-zsh"

alias zshconfig="xdg-open ~/.zshrc"
alias exr="cd ~/dev/exr2"
alias core="cd ~/dev/exr2/exr2_core"
alias base="cd ~/dev/exr2/exr2_base"
alias operation="cd ~/dev/exr2/exr2_operation"
alias comms="cd ~/dev/exr2/exr2_communications"
alias sim="cd ~/dev/exr2/exr2_simulation"

alias mv="mv -i" # Adds check on override

# Git
alias gc="git clone"
alias gs="git status"
alias gb="git branch -r"
alias gp="git push"

# Source Helper Scripts
#source ~/.dev/mcd.sh

#-------------------------------------------------------------------------
# History
#-------------------------------------------------------------------------
HISTSIZE=10000
SAVEHIST=10000
setopt append_history
setopt extended_history
setopt hist_expire_dups_first
setopt hist_ignore_dups # ignore duplication command history list
setopt hist_ignore_space
setopt hist_verify
setopt inc_append_history
setopt share_history # share command history data

# Ignore trivial commands in history
zshaddhistory() {
  local cmd="${1%%$'\n'*}"  # strip trailing newline
  local first="${cmd%% *}"
  case "$first" in
    ll|ls|la|clear|cd|man) return 1 ;;
  esac
  return 0   # add everything else
}

#-------------------------------------------------------------------------
# ROS 2 workspace autosource helper
# Assumes all exr2 workspaces are in current user's HOME
#-------------------------------------------------------------------------
_ros_autosource_exr2() {
    local root="$HOME/dev/exr2"
    local ws                                # iterator

    # Loops in alphabetical order for deterministic overlay stack
    for ws in "$root"/*(/) ; do

        # Ignore non‑directories (globbing safety)
        [[ -d $ws ]] || continue            # -d checks if it's a valid dir

        # Absolute path to this workspace’s setup file
        local setup_file="${ws%/}/install/setup.zsh"

        # Only source if the workspace is *built*
        if [[ -f $setup_file ]]; then       # -f checks if it's a valid file

            # Print to console
            printf "✔  overlaying %s\n" "${ws}"

            # shellcheck disable=SC1090
            source "$setup_file"
        fi
    done
}

#######################################################
#   Official ROS 2 environments
#######################################################
for setup in \
    /opt/ros/humble/setup.zsh \
    "$HOME/ros2_humble/install/setup.zsh"
do
[[ -f $setup ]] && source "$setup"
done

#######################################################
#   ROS 2 auto‑overlay for ExR2 workspaces
#######################################################
_ros_autosource_exr2

#######################################################
#  Things that need to happen last
#######################################################
source ~/.oh-my-zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
source ~/.oh-my-zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh




