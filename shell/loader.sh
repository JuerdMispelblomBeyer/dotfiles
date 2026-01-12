# Only run in interactive shells
case $- in
  *i*) ;;
  *) return 0 2>/dev/null || exit 0 ;;
esac

: "${DOTFILES_DIR:=$HOME/dotfiles}"

_source_if_exists() { [ -r "$1" ] && . "$1"; }
_source_if_exists "$DOTFILES_DIR/shell/ros2_autosource.sh"
if [ -n "${ZSH_VERSION:-}" ]; then
  _source_if_exists "$DOTFILES_DIR/ros/ros2_aliases.zsh"
  _source_if_exists "$DOTFILES_DIR/ros/ros2_utils.zsh"
elif [ -n "${BASH_VERSION:-}" ]; then
  _source_if_exists "$DOTFILES_DIR/ros/ros2_aliases.bash"
  _source_if_exists "$DOTFILES_DIR/ros/ros2_utils.bash"
else
  _source_if_exists "$DOTFILES_DIR/ros/ros2_aliases.bash"
  _source_if_exists "$DOTFILES_DIR/ros/ros2_utils.bash"
fi

# TODO Shell-agnostic helper
# _source_if_readable() { [ -r "$1" ] && . "$1"; }
# for f in "$DOTFILES_DIR"/shell/conf.d/*.sh; do # Source in a deterministic order
#   [ -e "$f" ] || continue
#   . "$f"
# done
