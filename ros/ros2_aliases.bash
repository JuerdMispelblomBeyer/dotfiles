#!/usr/bin/env bash

red()   { echo -e "\033[31m$1\033[m"; }
green() { echo -e "\033[32m$1\033[m"; }
cyan()  { echo -e "\033[36m$1\033[m"; }

ROS2_ALIASES="${BASH_SOURCE[0]}"
ROS2_ALIASES_DIR="$(cd "$(dirname "$ROS2_ALIASES")" && pwd)"

# set env function
setenvfile() {
  if [ -z "$1" ]; then
    local env_file="$ROS2_ALIASES_DIR/.env"
    if [ -n "${EDITOR:-}" ] && [ -f "$env_file" ]; then
      "$EDITOR" "$env_file"
    fi
    ROS2_ALIASES_ENV="$env_file"
  else
    ROS2_ALIASES_ENV="$1"
  fi

  if [ -f "$ROS2_ALIASES_ENV" ]; then
    while IFS='=' read -r key value; do
      # Skip comment lines and blank lines.
      [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue

      # Ignore comments on the right end.
      value=$(echo "$value" | sed 's/ #.*//')

      # Remove trailing spaces.
      value=$(echo "$value" | sed 's/[[:space:]]*$//')

      # Evaluate and expand commands part $().
      value=$(echo "$value" | sed -E 's/\$\([^)]*\)/$(eval echo \0)/g')

      # Expand environment variables part ${}.
      value=$(eval echo "\"$value\"")

      export "$key=$value"
    done < "$ROS2_ALIASES_ENV"
  else
    red "[ros2 aliases] This file not found : $ROS2_ALIASES_ENV"
    return 1
  fi
}

setenvfile "$ROS2_ALIASES_DIR/.env"

# source helper functions
# shellcheck source=./ros2_utils.bash
source "$ROS2_ALIASES_DIR/ros2_utils.bash"

# ros2 aliases help
rahelp() {
  green "--- set environments ---"
  echo "$(cyan setenvfile) : edit default env or load an argument env file"
  echo "$(cyan 'setrws PATH_TO_WORKSPACE') : set ROS 2 workspace"
  echo "$(cyan 'setrdi ROS_DOMAIN_ID') : set ROS_DOMAIN_ID and ROS_LOCALHOST_ONLY"
  echo "$(cyan 'setcbc COLCON_BUILD_COMMAND') : set colcon build command with its arguments"

  green "--- colcon build ---"
  echo "$(cyan cb)     : colcon build"
  echo "$(cyan cbcc)   : colcon build with clean cache"
  echo "$(cyan cbcf)   : colcon build with clean first"
  echo "$(cyan cbrm)   : colcon build after rm -rf build install log"
  echo "$(cyan cbp)    : colcon build with packages select"
  echo "$(cyan cbprm)  : colcon build with packages select after package cleanup"
  echo "$(cyan ctp)    : colcon test with packages select and verbose results"

  green "--- roscd ---"
  echo "$(cyan roscd)  : cd to the selected package"

  green "--- ROS CLI ---"
  echo "$(cyan rrun)   : ros2 run"
  echo "$(cyan rlaunch): ros2 launch"
  echo "$(cyan rnlist) : ros2 node list"
  echo "$(cyan rninfo) : ros2 node info"
  echo "$(cyan rtlist) : ros2 topic list"
  echo "$(cyan rtinfo) : ros2 topic info"
  echo "$(cyan rtecho) : ros2 topic echo"
  echo "$(cyan rplist) : ros2 param list"
  echo "$(cyan rpget)  : ros2 param get"
  echo "$(cyan rpset)  : ros2 param set"

  green "--- TF ---"
  echo "$(cyan 'view_frames (namespace)') : ros2 run tf2_tools view_frames"
  echo "$(cyan 'tf_echo [source_frame] [target_frame] (namespace)') : ros2 run tf2_ros tf2_echo"

  green "--- rosdep ---"
  echo "$(cyan rosdep_install) : rosdep install"

  green "--- current settings ---"
  echo "$(cyan ROS_WORKSPACE) : $ROS_WORKSPACE"
  echo "$(cyan ROS_DOMAIN_ID) : $ROS_DOMAIN_ID"
  echo "$(cyan COLCON_BUILD_CMD) : $COLCON_BUILD_CMD"
}

# set ROS 2 workspace
setrws() {
  local workspace_candidate="$1"
  if [ -z "$workspace_candidate" ]; then
    workspace_candidate=$(find "$HOME" -type d -name "*_ws" 2>/dev/null | fzf)
    [ -z "$workspace_candidate" ] && return
  fi
  if [ ! -d "$workspace_candidate/src" ]; then
    red "[ros2 aliases] No src directory in the workspace : $workspace_candidate"
    return
  fi
  cd "$workspace_candidate" || return
  ROS_WORKSPACE="$(pwd)"
  export ROS_WORKSPACE
  echo "$(cyan ROS_WORKSPACE) : $ROS_WORKSPACE"
}

# set colcon build
setcbc() {
  if [ $# -ne 1 ]; then
    red "[ros2 aliases] an argument is required. Usage: setcbc COLCON_BUILD_CMD"
    echo "current COLCON_BUILD_CMD=$(cyan "$COLCON_BUILD_CMD")"
    echo "default COLCON_BUILD_CMD=$(cyan "colcon build --symlink-install --parallel-workers $(nproc)")"
    return
  fi
  COLCON_BUILD_CMD="$1"
  export COLCON_BUILD_CMD
  echo "$(cyan COLCON_BUILD_CMD) : $COLCON_BUILD_CMD"
}

# set ROS_DOMAIN_ID
setrdi() {
  if [ $# -ne 1 ]; then
    red "[ros2 aliases] Usage: setrdi ROS_DOMAIN_ID"
    return
  fi

  if [ "$1" = "0" ]; then
    export ROS_LOCALHOST_ONLY=1
    export ROS_DOMAIN_ID=0
    echo "ROS_DOMAIN_ID=0"
    echo "ROS_LOCALHOST_ONLY=1"
  else
    export ROS_LOCALHOST_ONLY=0
    export ROS_DOMAIN_ID="$1"
    echo "ROS_DOMAIN_ID=$1"
    echo "ROS_LOCALHOST_ONLY=0"
  fi
}

# --- colcon build ---
_check_ROSWS_env() {
  if [ ! -d "$ROS_WORKSPACE/src" ]; then
    red "[ros2 aliases] No src directory in the workspace : $ROS_WORKSPACE"
    return 0
  fi
  return 1
}

colcon_build_command_exec() {
  pushd "$ROS_WORKSPACE" > /dev/null || return
  local cmd_str="$*"
  cyan "$cmd_str"
  _ros2_run_cmd "$cmd_str"
  if [ -f "./install/setup.bash" ]; then
    # shellcheck disable=SC1091
    source "./install/setup.bash"
  fi
  popd > /dev/null || return
}

cb() {
  _check_ROSWS_env && return
  colcon_build_command_exec "$COLCON_BUILD_CMD"
}

cbcc() {
  _check_ROSWS_env && return
  colcon_build_command_exec "$COLCON_BUILD_CMD --cmake-clean-cache"
}

cbcf() {
  _check_ROSWS_env && return
  local cmd="$COLCON_BUILD_CMD --cmake-clean-first"
  cyan "$cmd"
  local yn
  read -r -p "Do you want to execute? (y:Yes/n:No): " yn
  case "$yn" in
    [yY]*) ;;
    *) return ;;
  esac
  colcon_build_command_exec "$cmd"
}

cbrm() {
  _check_ROSWS_env && return
  local cmd="$COLCON_BUILD_CMD"
  cyan "rm -rf build install log && $cmd"
  local yn
  read -r -p "Do you want to execute? (y:Yes/n:No): " yn
  case "$yn" in
    [yY]*) ;;
    *) return ;;
  esac
  rm -rf build install log
  colcon_build_command_exec "$cmd"
}

_ros_pkg_names() {
  find "$ROS_WORKSPACE/src" -name "package.xml" -print0 2>/dev/null |
    while IFS= read -r -d '' file; do
      grep -oP '(?<=<name>).*?(?=</name>)' "$file"
    done
}

cbp() {
  _check_ROSWS_env && return
  local pkg_name="$*"
  if [ -z "$pkg_name" ]; then
    pkg_name=$(_ros_pkg_names | fzf)
    [ -z "$pkg_name" ] && return
  fi
  colcon_build_command_exec "$COLCON_BUILD_CMD --packages-select $pkg_name"
}

cbprm() {
  _check_ROSWS_env && return
  local pkg_names="$*"
  if [ -z "$pkg_names" ]; then
    pkg_names=$(_ros_pkg_names | fzf)
    [ -z "$pkg_names" ] && return
  fi

  local cmd="$COLCON_BUILD_CMD --packages-select $pkg_names"
  cyan "rm -rf build/pkgs install/pkgs log/pkgs && $cmd"
  cyan "pkgs : $pkg_names"

  local yn
  read -r -p "Do you want to execute? (y:Yes/n:No): " yn
  case "$yn" in
    [yY]*) ;;
    *) return ;;
  esac

  local pkg_name
  for pkg_name in $pkg_names; do
    rm -rf "$ROS_WORKSPACE/build/$pkg_name"
    rm -rf "$ROS_WORKSPACE/install/$pkg_name"
    rm -rf "$ROS_WORKSPACE/log/$pkg_name"
  done

  colcon_build_command_exec "$cmd"
}

ctp() {
  _check_ROSWS_env && return
  local pkg_name="$*"
  if [ -z "$pkg_name" ]; then
    pkg_name=$(_ros_pkg_names | fzf)
    [ -z "$pkg_name" ] && return
  fi

  pushd "$ROS_WORKSPACE" > /dev/null || return
  cbp "$pkg_name"
  local cmd="colcon test --parallel-workers $(nproc) --packages-select $pkg_name"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
  cmd="colcon test-result --verbose"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
  popd > /dev/null || return
}

_pkg_name_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local opts
  opts=$(_ros_pkg_names)
  COMPREPLY=($(compgen -W "$opts" -- "$cur"))
}
if command -v complete >/dev/null 2>&1; then
  complete -F _pkg_name_complete cbp cbprm ctp
fi

# --- roscd ---
roscd() {
  _check_ROSWS_env && return
  local pkg_dir_name="$1"
  if [ -z "$pkg_dir_name" ]; then
    pkg_dir_name=$(find "$ROS_WORKSPACE/src" -name "package.xml" -printf "%h\n" 2>/dev/null | awk -F/ '{print $NF}' | fzf)
    [ -z "$pkg_dir_name" ] && cd "$ROS_WORKSPACE" && return
  fi

  local pkg_dir
  pkg_dir=$(find "$ROS_WORKSPACE/src" -name "$pkg_dir_name" 2>/dev/null |
    awk '{print length(), $0}' | sort -n | awk '{print $2}' | head -n 1)
  [ -z "$pkg_dir" ] && red "[ros2 aliases] No such package : $pkg_dir_name" && return
  cd "$pkg_dir" || return
}

_pkg_directory_complete() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local opts
  opts=$(find "$ROS_WORKSPACE/src" -name "package.xml" -printf "%h\n" 2>/dev/null | awk -F/ '{print $NF}')
  COMPREPLY=($(compgen -W "$opts" -- "$cur"))
}
if command -v complete >/dev/null 2>&1; then
  complete -F _pkg_directory_complete roscd
fi

# --- rosdep ---
rosdep_install() {
  _check_ROSWS_env && return
  pushd "$ROS_WORKSPACE" > /dev/null || return
  cyan "rosdep install --from-paths src --ignore-src -y"
  rosdep install --from-paths src --ignore-src -y
  popd > /dev/null || return
}

# --- pkg ---
alias rpkgexe="ros2 pkg executables"

# --- ros2 launch ---
rlaunch() {
  _check_ROSWS_env && return

  local pkg_name
  pkg_name=$(find "/opt/ros/$ROS_DISTRO/share" "$ROS_WORKSPACE/src" -name "package.xml" -print0 2>/dev/null |
    while IFS= read -r -d '' file; do
      grep -oP '(?<=<name>).*?(?=</name>)' "$file"
    done | fzf)
  [ -z "$pkg_name" ] && return

  local pkg_dir
  pkg_dir=$(find "/opt/ros/$ROS_DISTRO/share" "$ROS_WORKSPACE/install" -name "$pkg_name" 2>/dev/null |
    awk '{print length(), $0}' | sort -n | awk '{print $2}' | head -n 1)
  [ ! -d "$pkg_dir/launch" ] && red "[ros2 aliases] No launch directory : $pkg_name" && return

  local launch_file
  launch_file=$(find "$pkg_dir" -regextype posix-extended -regex '.*launch.*\.(py|xml|yaml)' -exec basename {} \; | fzf)
  [ -z "$launch_file" ] && return

  local cmd="ros2 launch $pkg_name $launch_file"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}
