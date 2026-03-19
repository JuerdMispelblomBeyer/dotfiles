# Shell-agnostic ROS 2 lazy-load helpers for bash and zsh.

_ros2_setup_suffix() {
  if [ -n "${ZSH_VERSION-}" ]; then
    printf '%s' 'zsh'
    return
  fi
  if [ -n "${BASH_VERSION-}" ]; then
    printf '%s' 'bash'
    return
  fi
  case "${SHELL-}" in
    */zsh) printf '%s' 'zsh' ;;
    */bash) printf '%s' 'bash' ;;
    *) printf '%s' 'bash' ;;
  esac
}

_ros2_aliases_file() {
  dotfiles_dir=${DOTFILES_DIR:-"$HOME/dotfiles"}
  if [ -n "${ZSH_VERSION-}" ]; then
    printf '%s' "$dotfiles_dir/ros/ros2_aliases.zsh"
    return
  fi
  printf '%s' "$dotfiles_dir/ros/ros2_aliases.bash"
}

ros2_source_base() {
  [ -n "${ROS2_BASE_SOURCED-}" ] && return 0

  ros2_setup_ext=$(_ros2_setup_suffix)
  ros2_distro=${ROS2_DEFAULT_DISTRO:-humble}
  ros2_setup_file="/opt/ros/$ros2_distro/setup.$ros2_setup_ext"

  if [ ! -f "$ros2_setup_file" ]; then
    printf '[ros2] setup file not found: %s\n' "$ros2_setup_file" >&2
    return 1
  fi

  . "$ros2_setup_file" || return 1
  ROS2_BASE_SOURCED=1
}

ros2_source_aliases() {
  [ -n "${ROS2_ALIASES_SOURCED-}" ] && return 0

  ros2_aliases_file=$(_ros2_aliases_file)
  if [ ! -f "$ros2_aliases_file" ]; then
    printf '[ros2] aliases file not found for this shell: %s\n' "$ros2_aliases_file" >&2
    return 1
  fi

  . "$ros2_aliases_file" || return 1
  ROS2_ALIASES_SOURCED=1
}

ros2_autosource() {
  ros2_source_base || return 1
  ros2_source_aliases || return 1
}
