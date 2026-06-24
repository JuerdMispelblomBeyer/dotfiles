#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
backup_suffix=".pre-dotfiles-backup-$(date +%Y%m%d%H%M%S)"

link_file() {
  local repo_path="$1"
  local home_path="$2"
  local source_path="$repo_dir/$repo_path"
  local target_path="$HOME/$home_path"

  mkdir -p "$(dirname "$target_path")"

  if [[ -L "$target_path" && "$(readlink -f "$target_path")" == "$source_path" ]]; then
    return
  fi

  if [[ -e "$target_path" || -L "$target_path" ]]; then
    mv "$target_path" "$target_path$backup_suffix"
  fi

  ln -s "$source_path" "$target_path"
}

link_file bash/.bashrc .bashrc
link_file zsh/.zshrc .zshrc
link_file ssh/config .ssh/config
link_file git/gitconfig .gitconfig
link_file fish/config.fish .config/fish/config.fish
link_file fish/fish_variables .config/fish/fish_variables
link_file vscode/settings.json .config/Code/User/settings.json
link_file vscode/mcp.json .config/Code/User/mcp.json
link_file htop/htoprc .config/htop/htoprc
link_file gtk/gtk-3.0/settings.ini .config/gtk-3.0/settings.ini
link_file gtk/gtk-4.0/settings.ini .config/gtk-4.0/settings.ini
link_file xdg/user-dirs.dirs .config/user-dirs.dirs
link_file codex/config.toml .codex/config.toml
link_file claude/settings.json .claude/settings.json
link_file gazebo/gui.ini .gazebo/gui.ini
link_file ros/rqt_gui.ini .config/ros.org/rqt_gui.ini
