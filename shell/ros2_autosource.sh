# Shell-agnostic ROS 2 autosource helpers for bash and zsh.

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

ros2_source_base() {
  [ -n "${ROS2_BASE_SOURCED-}" ] && return 0
  ROS2_BASE_SOURCED=1

  ros2_setup_ext=$(_ros2_setup_suffix)
  for setup in /opt/ros/humble/setup."$ros2_setup_ext" \
               "$HOME/ros2_humble/install/setup.$ros2_setup_ext"
  do
    [ -f "$setup" ] && . "$setup"
  done
}

ros2_autosource_exr2() {
  [ -n "${ROS2_AUTOSOURCE_DONE-}" ] && return 0
  ROS2_AUTOSOURCE_DONE=1

  ros2_setup_ext=$(_ros2_setup_suffix)
  ros2_root=${ROS2_EXR2_ROOT:-"$HOME/dev/exr2"}

  if [ -n "${ZSH_VERSION-}" ]; then
    setopt local_options nonomatch 2>/dev/null
  fi

  for ws in "$ros2_root"/*; do
    [ -d "$ws" ] || continue
    setup_file="$ws/install/setup.$ros2_setup_ext"
    if [ -f "$setup_file" ]; then
      printf '[ros2] overlaying %s\n' "$ws"
      . "$setup_file"
    fi
  done
}

ros2_autosource() {
  ros2_source_base
  ros2_autosource_exr2
}
