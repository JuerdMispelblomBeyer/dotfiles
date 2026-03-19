#!/usr/bin/env bash

# based on https://github.com/tonynajjar/ros2-aliases

cyan() { echo -e "\033[36m$1\033[m"; }

_ros2_run_cmd() {
  local cmd_str="$1"
  eval "$cmd_str"
}

# ROS 2 run

rrun() {
  if [ $# -eq 0 ]; then
    local pkg_name
    pkg_name=$(ros2 pkg list | fzf)
    [ -z "$pkg_name" ] && return
    rrun "$pkg_name"
  elif [ $# -eq 1 ]; then
    local pkg_and_exe
    pkg_and_exe=$(ros2 pkg executables | grep "$1" | fzf)
    [ -z "$pkg_and_exe" ] && return
    local cmd="ros2 run $pkg_and_exe"
    cyan "$cmd"
    _ros2_run_cmd "$cmd"
  fi
}

# Topics

rtlist() {
  local cmd="ros2 topic list"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

rtecho() {
  local topic
  topic=$(ros2 topic list | fzf)
  [ -z "$topic" ] && return
  local cmd="ros2 topic echo $topic"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

rtinfo() {
  local topic
  topic=$(ros2 topic list | fzf)
  [ -z "$topic" ] && return
  local cmd="ros2 topic info -v $topic"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

rtbw() {
  local topic
  topic=$(ros2 topic list | fzf)
  [ -z "$topic" ] && return
  local cmd="ros2 topic bw $topic"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

# Nodes

rnlist() {
  local cmd="ros2 node list"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

rninfo() {
  local node
  node=$(ros2 node list | fzf)
  [ -z "$node" ] && return
  local cmd="ros2 node info $node"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

rnkill() {
  local node_to_kill_raw
  node_to_kill_raw=$(ros2 node list | fzf)
  [ -z "$node_to_kill_raw" ] && return

  local node_to_kill="${node_to_kill_raw##*/}"
  [ -z "$node_to_kill" ] && return
  node_to_kill="[${node_to_kill:0:1}]${node_to_kill:1}"

  # Parse PID and kill only when one matching process exists.
  local proc_nb
  proc_nb=$(ps aux | grep "[/]$node_to_kill" | wc -l)
  if [ "$proc_nb" -gt 1 ]; then
    echo "This node name matched with more than 1 process. Not killing"
    return
  elif [ "$proc_nb" -eq 0 ]; then
    echo "No processes found matching this node name"
    return
  fi

  local proc_pid
  proc_pid=$(ps aux | grep "[/]$node_to_kill" | awk '{print $2}')
  local cmd="kill $proc_pid"
  echo "Killing $node_to_kill_raw with PID $proc_pid"
  _ros2_run_cmd "$cmd"
}

# Services

rslist() {
  local cmd="ros2 service list"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

# Parameters

rplist() {
  local node
  node=$(ros2 node list | fzf)
  [ -z "$node" ] && return
  local cmd="ros2 param list $node --param-type"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

rpget() {
  local node
  node=$(ros2 node list | fzf)
  [ -z "$node" ] && return
  local param
  param=$(ros2 param list "$node" | fzf)
  [ -z "$param" ] && return
  local cmd="ros2 param get $node $param"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

rpset() {
  local node
  node=$(ros2 node list | fzf)
  [ -z "$node" ] && return
  local param
  param=$(ros2 param list "$node" | fzf)
  [ -z "$param" ] && return
  echo -n "value: "
  local value
  read -r value
  local cmd="ros2 param set $node $param $value"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

# Interface

rishow() {
  local interface
  interface=$(ros2 interface list | fzf)
  [ -z "$interface" ] && return
  local cmd="ros2 interface show $interface"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

# TF

view_frames() {
  local remap=""
  if [ $# -ne 0 ]; then
    remap="--ros-args -r /tf:=/$1/tf -r /tf_static:=/$1/tf_static"
  fi
  local cmd="ros2 run tf2_tools view_frames $remap"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

tf_echo() {
  local remap=""
  if [ $# -eq 3 ]; then
    remap="--ros-args -r /tf:=/$3/tf -r /tf_static:=/$3/tf_static"
  fi
  local cmd="ros2 run tf2_ros tf2_echo $1 $2 $remap"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

# Colcon

cb() {
  local cmd="colcon build --symlink-install"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

cbp() {
  local cmd
  if [ $# -eq 0 ]; then
    local package
    package=$(colcon list -n | fzf)
    [ -z "$package" ] && return
    cmd="colcon build --symlink-install --packages-select $package"
  else
    cmd="colcon build --symlink-install --packages-select $*"
  fi
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

cl() {
  local cmd="colcon list -n"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}

# Rosdep

rosdep_install() {
  local cmd="rosdep install --from-paths src --ignore-src -r -y"
  cyan "$cmd"
  _ros2_run_cmd "$cmd"
}
