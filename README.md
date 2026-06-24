# Dotfiles

Personal Linux configuration files. The repo is intended to live at
`~/dotfiles`, with selected files symlinked into their normal locations.

## Fresh Install

Install the basic tools first:

```sh
sudo apt update
sudo apt install git bash zsh openssh-client
```

Clone the repo to the expected location:

```sh
git clone git@github.com:JuerdMispelblomBeyer/dotfiles.git ~/dotfiles
cd ~/dotfiles
```

Create the symlinks:

```sh
./tools/link_configs.sh
```

The script is safe to rerun. If a managed config file already exists and is not
already linked to this repo, it is moved aside with a timestamped suffix like:

```text
.pre-dotfiles-backup-20260624143000
```

## Managed Files

`tools/link_configs.sh` currently manages these links:

| Repo file | Installed as |
| --- | --- |
| `bash/.bashrc` | `~/.bashrc` |
| `zsh/.zshrc` | `~/.zshrc` |
| `ssh/config` | `~/.ssh/config` |
| `git/gitconfig` | `~/.gitconfig` |
| `fish/config.fish` | `~/.config/fish/config.fish` |
| `fish/fish_variables` | `~/.config/fish/fish_variables` |
| `vscode/settings.json` | `~/.config/Code/User/settings.json` |
| `vscode/mcp.json` | `~/.config/Code/User/mcp.json` |
| `htop/htoprc` | `~/.config/htop/htoprc` |
| `gtk/gtk-3.0/settings.ini` | `~/.config/gtk-3.0/settings.ini` |
| `gtk/gtk-4.0/settings.ini` | `~/.config/gtk-4.0/settings.ini` |
| `xdg/user-dirs.dirs` | `~/.config/user-dirs.dirs` |
| `codex/config.toml` | `~/.codex/config.toml` |
| `claude/settings.json` | `~/.claude/settings.json` |
| `gazebo/gui.ini` | `~/.gazebo/gui.ini` |
| `ros/rqt_gui.ini` | `~/.config/ros.org/rqt_gui.ini` |

The Bash and Zsh configs set `DOTFILES_DIR="$HOME/dotfiles"` and source
`shell/loader.sh`, which loads shared aliases and ROS helper functions.

## After Installing

Optional tools used by these configs:

```sh
sudo apt install htop fish
```

Zsh expects Oh My Zsh and these plugins if you use that shell:

```sh
git clone https://github.com/ohmyzsh/ohmyzsh.git ~/.oh-my-zsh
git clone https://github.com/zsh-users/zsh-autosuggestions.git ~/.oh-my-zsh/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ~/.oh-my-zsh/plugins/zsh-syntax-highlighting
```

Switch the login shell if needed:

```sh
chsh -s "$(command -v zsh)"
```

## Adding More Configs

1. Copy the config file into a suitable directory in this repo.
2. Add a `link_file repo/path home/path` line to `tools/link_configs.sh`.
3. Run `bash -n tools/link_configs.sh`.
4. Run `./tools/link_configs.sh` and verify the new symlink.
5. Commit the new file and script update.

Avoid committing secrets, private keys, cookies, browser profiles, auth tokens,
machine IDs, caches, generated histories, or large application state.
