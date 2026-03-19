#!/usr/bin/env zsh

function red   { echo -e "\033[31m$1\033[m"; }
function green { echo -e "\033[32m$1\033[m"; }
function cyan  { echo -e "\033[36m$1\033[m"; }

ROS2_ALIASES=${(%):-%N}
ROS2_ALIASES=${ROS2_ALIASES:A}
ROS2_ALIASES_DIR=${ROS2_ALIASES:h}

# set env function
function setenvfile {
  if [ -z $1 ]; then
    editor $ROS2_ALIASES_DIR/.env
    ROS2_ALIASES_ENV=$ROS2_ALIASES_DIR/.env
  else
    ROS2_ALIASES_ENV=$1
  fi
  if [ -f "$ROS2_ALIASES_ENV" ]; then
    while IFS='=' read -r key value; do
      # Skip comment lines and blank lines
      if [[ "$key" =~ ^#.* || -z "$key" ]]; then
          continue
      fi
      # Ignore comments on the right end 
      value=$(echo "$value" | sed 's/ #.*//')
      # Remove trailing spaces (including newlines)
      value=$(echo "$value" | sed 's/[[:space:]]*$//')
      # Evaluate and expand commands part $() 
      value=$(echo "$value" | sed -E 's/\$\([^)]*\)/$(eval echo \0)/g')
      # Expand environment variables part ${} 
      value=$(eval echo "\"$value\"")
      export $key="$value"
    done < $ROS2_ALIASES_ENV
  else
    red "[ros2 aliases] This file not found. : $ROS2_ALIASES_ENV"
    return 1
  fi
}

# cp -n $ROS2_ALIASES_DIR/.env_example $ROS2_ALIASES_DIR/.env
setenvfile $ROS2_ALIASES_DIR/.env

# source helper functions
source "$ROS2_ALIASES_DIR/ros2_utils.zsh"

# ros2 aliases help
function rahelp {
  green "--- set environments ---"
  echo "`cyan setenvfile` : edit default env or load an argument env file"
  echo "`cyan setrws\ PATH_TO_WORKSPACE` : set ROS 2 workspace"
  echo "`cyan setrdi\ ROS_DOMAIN_ID` : set ROS_DOMAIN_ID and ROS_LOCALHOST_ONLY"
  echo "`cyan setcbc\ COLCON_BUILD_COMMAND` : set colcon build command with its arguments"
  green "--- colcon build ---"
  echo "`cyan cb`     : colcon build"
  echo "`cyan cbcc`   : colcon build with clean cache"
  echo "`cyan cbcf`   : colcon build with clean first"
  echo "`cyan cbrm`   : colcon build after rm -rf build install log"
  echo "`cyan cbp`    : colcon build with packages select (Both fzf and tab completion are valid)"
  echo "`cyan cbprm`  : colcon build with packages select after rm -rf build install log for selected packages"
  echo "`cyan ctp`    : colcon test with packages select and colcon test-result --verbose"
  green "--- roscd ---"
  echo "`cyan roscd`  : cd to the selected package (Both fzf and tab completion are valid)"
  green "--- ROS CLI ---"
  echo "`cyan rrun`  : ros2 run"
  echo "`cyan rlaunch`  : ros2 launch"
  echo "`cyan rnlist` : ros2 node list"
  echo "`cyan rninfo` : ros2 node info"
  echo "`cyan rtlist` : ros2 topic list"
  echo "`cyan rtinfo` : ros2 topic info"
  echo "`cyan rtecho` : ros2 topic echo"
  echo "`cyan rplist` : ros2 param list"
  echo "`cyan rpget`  : ros2 param get"
  echo "`cyan rpset`  : ros2 param set"
  green "--- TF ---"
  echo "`cyan view_frames\ \(namespace\)` : ros2 run tf2_tools view_frames"
  echo "`cyan tf_echo\ \[source_frame\]\ \[target_frame\]\ \(namespace\)` : ros2 run tf2_ros tf2_echo"
  green "--- rosdep ---"
  echo "`cyan rosdep_install` : rosdep install"
  green "--- offical ---"
  echo "`cyan "ros2 -h"` : The Official help"
  green "--- current settings ---"
  echo "`cyan ROS_WORKSPACE` : "$ROS_WORKSPACE""
  echo "`cyan ROS_DOMAIN_ID` : "$ROS_DOMAIN_ID""
  echo "`cyan COLCON_BUILD_CMD` : "$COLCON_BUILD_CMD""
}

# set ROS 2 workspace
function setrws {
  local workspace_candidate=$1
  if [ -z "$1" ]; then
    workspace_candidate=$(find $HOME -type d -name "*_ws" | fzf)
    [[ -z "$workspace_candidate" ]] && return
  fi
  if [ ! -d "$workspace_candidate/src" ]; then
    red "[ros2 aliases] No src directory in the workspace : $workspace_candidate"
    return
  fi
  cd $workspace_candidate
  ROS_WORKSPACE=$(pwd)
  echo "`cyan ROS_WORKSPACE` : "$ROS_WORKSPACE""
  print -s -- "setrws $ROS_WORKSPACE"
}

# set colcon build
function setcbc {
  if [ $# != 1 ]; then
    red "[ros2 aliases] an argument is required. Usage: setcbc COLCON_BUILD_CMD"
    echo "current COLCON_BUILD_CMD=\"`cyan "$COLCON_BUILD_CMD"`\""
    echo "default COLCON_BUILD_CMD=\"`cyan "colcon build --symlink-install --parallel-workers $(nproc)"`\""
    return
  fi
  source $ROS2_ALIASES "$ROS_WORKSPACE" "$1"
}

# set ROS_DOMAIN_ID
function setrdi {
  if [ $# != 1 ] || [ $1 -eq 0 ]; then
    export ROS_LOCALHOST_ONLY=1
    echo "ROS_DOMAIN_ID=$1"
    echo "ROS_LOCALHOST_ONLY=1"
  else
    export ROS_LOCALHOST_ONLY=0
    export ROS_DOMAIN_ID=$1
    echo "ROS_DOMAIN_ID=$1"
  fi
}

# ---colcon build---
function _check_ROSWS_env() {
  if [ ! -d "$ROS_WORKSPACE/src" ]; then
    red "[ros2 aliases] No src directory in the workspace : $workspace_candidate"
    return 0
  fi
  return 1
}

function colcon_build_command_exec {
  pushd $ROS_WORKSPACE > /dev/null
  local cmd_str="$*"
  cyan "$cmd_str"
  _ros2_run_cmd "$cmd_str"
  source ./install/setup.zsh
  popd > /dev/null
}

function cb {
  _check_ROSWS_env && return
  colcon_build_command_exec "$COLCON_BUILD_CMD"
}

function cbcc {
  _check_ROSWS_env && return
  colcon_build_command_exec "$COLCON_BUILD_CMD --cmake-clean-cache"
}

function cbcf {
  _check_ROSWS_env && return
  local cmd="$COLCON_BUILD_CMD --cmake-clean-first"
  cyan "$cmd"
  read -r "yn?Do you want to execute? (y:Yes/n:No): "
  case "$yn" in
    [yY]*);;
    *) return ;;
  esac
  colcon_build_command_exec "$cmd"
}

function cbrm {
  _check_ROSWS_env && return
  local cmd="$COLCON_BUILD_CMD"
  cyan "rm -rf build install log && $cmd"
  read -r "yn?Do you want to execute? (y:Yes/n:No): "
  case "$yn" in
    [yY]*);;
    *) return ;;
  esac
  rm -rf build install log
  colcon_build_command_exec "$cmd"
}

function cbp {
  _check_ROSWS_env && return
  local pkg_name="$@"
  if [ -z "$1" ]; then
    pkg_name=$(find $ROS_WORKSPACE/src -name "package.xml" -print0 | while IFS= read -r -d '' file; do grep -oP '(?<=<name>).*?(?=</name>)' "$file"; done | fzf)
    [[ -z "$pkg_name" ]] && return
  fi
  colcon_build_command_exec "$COLCON_BUILD_CMD --packages-select $pkg_name"
  print -s -- "cbp $pkg_name"
}

function cbprm {
  _check_ROSWS_env && return
  local pkg_names="$@"
  if [ -z "$1" ]; then
    pkg_names=$(find $ROS_WORKSPACE/src -name "package.xml" -print0 | while IFS= read -r -d '' file; do grep -oP '(?<=<name>).*?(?=</name>)' "$file"; done | fzf)
    [[ -z "$pkg_names" ]] && return
  fi
  local cmd="$COLCON_BUILD_CMD --packages-select $pkg_names"
  cyan "rm -rf build/pkgs install/pkgs log/pkgs && $cmd"
  cyan "pkgs : $pkg_names"
  read -r "yn?Do you want to execute? (y:Yes/n:No): "
  case "$yn" in
    [yY]*);;
    *) return ;;
  esac
  for pkg_name in $pkg_names; do
    rm -rf $ROS_WORKSPACE/build/$pkg_name
    rm -rf $ROS_WORKSPACE/install/$pkg_name
    rm -rf $ROS_WORKSPACE/log/$pkg_name
  done
  colcon_build_command_exec "$cmd"
}

function ctp {
  _check_ROSWS_env && return
  local pkg_name="$@"
  if [ -z "$1" ]; then
    pkg_name=$(find $ROS_WORKSPACE/src -name "package.xml" -print0 | while IFS= read -r -d '' file; do grep -oP '(?<=<name>).*?(?=</name>)' "$file"; done | fzf)
    [[ -z "$pkg_name" ]] && return
  fi
  pushd $ROS_WORKSPACE > /dev/null
  cbp $pkg_name
  local cmd="colcon test --parallel-workers $(nproc) --packages-select $pkg_name"
  cyan "$cmd" && _ros2_run_cmd "$cmd"
  cmd="colcon test-result --verbose"
  cyan "$cmd" && _ros2_run_cmd "$cmd"
  print -s -- "ctp $pkg_name"
  popd > /dev/null
}
_pkg_name_complete() {
  local -a pkg_names
  pkg_names=("${(f)$(find $ROS_WORKSPACE/src -name "package.xml" -print0 | while IFS= read -r -d '' file; do grep -oP '(?<=<name>).*?(?=</name>)' "$file"; done)}")
  compadd -- $pkg_names
}
if command -v compdef >/dev/null; then
  compdef _pkg_name_complete cbp cbprm ctp
fi

# ---roscd---
function roscd {
  _check_ROSWS_env && return
  local pkg_dir_name=$1
  if [ -z "$1" ]; then
    pkg_dir_name=$(find $ROS_WORKSPACE/src -name "package.xml" -printf "%h\n" | awk -F/ '{print $NF}' | fzf)
    [[ -z "$pkg_dir_name" ]] && cd $ROS_WORKSPACE && return
    print -s -- "roscd $pkg_dir_name"
  fi
  local pkg_dir=$(find $ROS_WORKSPACE/src -name $pkg_dir_name | awk '{print length() ,$0}' | sort -n | awk '{ print  $2 }' | head -n 1)
  [[ -z $pkg_dir ]] && red "[ros2 aliases] No such package : $pkg_dir_name" && return
  cd $pkg_dir
}
_pkg_directory_complete() {
  local -a pkg_dir_names
  pkg_dir_names=("${(f)$(find $ROS_WORKSPACE/src -name "package.xml" -printf "%h\n" | awk -F/ '{print $NF}')}")
  compadd -- $pkg_dir_names
}
if command -v compdef >/dev/null; then
  compdef _pkg_directory_complete roscd
fi

# ---rosdep---
function rosdep_install {
  _check_ROSWS_env && return
  pushd $ROS_WORKSPACE > /dev/null
  cyan "rosdep install --from-paths src --ignore-src -y"
  rosdep install --from-paths src --ignore-src -y
  source /opt/ros/$ROS_DISTRO/setup.zsh
  popd > /dev/null
}

# ---pkg---
alias rpkgexe="ros2 pkg executables"

# ---ros2 launch---
function rlaunch {
  _check_ROSWS_env && return
  local pkg_name=$(find /opt/ros/$ROS_DISTRO/share $ROS_WORKSPACE/src -name "package.xml" -print0 | while IFS= read -r -d '' file; do grep -oP '(?<=<name>).*?(?=</name>)' "$file"; done | fzf)
  [[ -z "$pkg_name" ]] && return
  local pkg_dir=$(find /opt/ros/$ROS_DISTRO/share $ROS_WORKSPACE/install -name $pkg_name | awk '{print length(), $0}' | sort -n | awk '{ print  $2 }' | head -n 1)
  [[ -z "$pkg_dir/launch" ]] && red "[ros2 aliases] No launch directory : $pkg_name" && return
  local launch_file=$(find $pkg_dir -regex ".*launch*\.\(py\|xml\|yaml\)" -exec basename {} \; | awk -F/ '{print $NF}' | fzf)
  [[ -z $launch_file ]] && return
  local cmd="ros2 launch $pkg_name $launch_file"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
  print -s -- "rlaunch"
  print -s -- "$cmd"
}
