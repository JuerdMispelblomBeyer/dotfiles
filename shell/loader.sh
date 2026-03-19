# Only run in interactive shells
case $- in
  *i*) ;;
  *) return 0 2>/dev/null || exit 0 ;;
esac

: "${DOTFILES_DIR:=$HOME/dotfiles}"

_source_if_exists() { [ -r "$1" ] && . "$1"; }
_source_if_exists "$DOTFILES_DIR/shell/ros2_autosource.sh"

if command -v ros2_autosource >/dev/null 2>&1; then
  ros() {
    ros2_autosource "$@"
  }
fi

# TODO Shell-agnostic helper
# _source_if_readable() { [ -r "$1" ] && . "$1"; }
# for f in "$DOTFILES_DIR"/shell/conf.d/*.sh; do # Source in a deterministic order
#   [ -e "$f" ] || continue
#   . "$f"
# done
