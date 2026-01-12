#!/usr/bin/env zsh

# based on https://github.com/tonynajjar/ros2-aliases

function cyan  { echo -e "\033[36m$1\033[m"; }

function _ros2_run_cmd {
  local cmd_str="$1"
  local -a cmd
  cmd=(${=cmd_str})
  $cmd
}

# ROS 2 run

function rrun {
  if [ $# -eq 0 ]; then
    local PKG_NAME=$(ros2 pkg list | fzf)
    [[ -z "$PKG_NAME" ]] && return
    print -s -- "rrun $PKG_NAME"
    rrun $PKG_NAME
  elif [ $# -eq 1 ]; then
    local PKG_AND_EXE=$(ros2 pkg executables | grep $1 | fzf)
    [[ -z "$PKG_AND_EXE" ]] && return
    local CMD="ros2 run $PKG_AND_EXE"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rrun"
    print -s -- "$CMD"
  fi
}

# Topics

function rtlist {
    local CMD="ros2 topic list"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rtlist"
    print -s -- "$CMD"
}

function rtecho {
    local TOPIC=$(ros2 topic list | fzf)
    [[ -z "$TOPIC" ]] && return
    CMD="ros2 topic echo $TOPIC"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rtecho"
    print -s -- "$CMD"
}

function rtinfo {
    local TOPIC=$(ros2 topic list | fzf)
    [[ -z "$TOPIC" ]] && return
    local CMD="ros2 topic info -v $TOPIC"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rtinfo"
    print -s -- "$CMD"
}

function rtbw {
    local TOPIC=$(ros2 topic list | fzf)
    [[ -z "$TOPIC" ]] && return
    local CMD="ros2 topic bw $TOPIC"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rtbw"
    print -s -- "$CMD"
}

# Nodes

function rnlist {
    local CMD="ros2 node list"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rnlist"
    print -s -- "$CMD"
}

function rninfo {
    local NODE=$(ros2 node list | fzf)
    [[ -z "$NODE" ]] && return
    local CMD="ros2 node info $NODE"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rninfo"
    print -s -- "$CMD"
}

function rnkill {
    local NODE_TO_KILL_RAW=$(ros2 node list | fzf)
    [[ -z "$NODE_TO_KILL_RAW" ]] && return
    local -a NODE_TO_KILL=(${(s:/:)NODE_TO_KILL_RAW})
    NODE_TO_KILL=${NODE_TO_KILL[-1]} # extract last word from node name
    NODE_TO_KILL="[${NODE_TO_KILL[1]}]${NODE_TO_KILL[2,-1]}"
    # The method used is to parse the PID and use kill <PID>.
    # If more than 1 PID is found, we abort to avoid killing other processes.
    # The parsing checks for any process with the string [/]$NODE_TO_KILL.
    # This can probably be optimized to always find the one node we are looking for.
    local PROC_NB=$(ps aux | grep [/]$NODE_TO_KILL | wc -l)
    if [ $PROC_NB -gt 1 ]; then
        echo "This node name matched with more than 1 process. Not killing"
        return
    elif [ $PROC_NB -eq 0 ]; then
        echo "No processes found matching this node name"
        return
    fi
    local PROC_PID=$(ps aux | grep [/]$NODE_TO_KILL | awk '{print $2}')
    local CMD="kill $PROC_PID"
    echo "Killing $NODE_TO_KILL_RAW with PID $PROC_PID"
    _ros2_run_cmd "$CMD"
    print -s -- "rnlist"
    print -s -- "$CMD"
}

# Services

function rslist {
    local CMD="ros2 service list"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rslist"
    print -s -- "$CMD"
}

# Parameters

function rplist {
    local NODE=$(ros2 node list | fzf)
    [[ -z "$NODE" ]] && return
    local CMD="ros2 param list $NODE --param-type"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rplist"
    print -s -- "$CMD"
}

function rpget {
    local NODE=$(ros2 node list | fzf)
    [[ -z "$NODE" ]] && return
    local PARAM=$(ros2 param list $NODE | fzf)
    [[ -z "$PARAM" ]] && return
    local CMD="ros2 param get $NODE $PARAM"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rpget"
    print -s -- "$CMD"
}

function rpset {
    local NODE=$(ros2 node list | fzf)
    [[ -z "$NODE" ]] && return
    local PARAM=$(ros2 param list $NODE | fzf)
    [[ -z "$PARAM" ]] && return
    echo -n "value: "
    read VALUE
    local CMD="ros2 param set $NODE $PARAM $VALUE"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rpset"
    print -s -- "$CMD"
}

# Interface

function rishow {
  local INTERFACE=$(ros2 interface list | fzf)
  [[ -z "$INTERFACE" ]] && return
  local CMD="ros2 interface show $INTERFACE"
  cyan "$CMD"
  _ros2_run_cmd "$CMD"
  print -s -- "rishow"
  print -s -- "$CMD"
}

# TF

function view_frames {
    if [ $# -eq 0 ]; then
        local REMAP=""
    else
        local REMAP="--ros-args -r /tf:=/$1/tf -r /tf_static:=/$1/tf_static"
    fi
    local CMD="ros2 run tf2_tools view_frames $REMAP"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "view_frames $*"
    print -s -- "$CMD"
}

function tf_echo {
    if [ $# -eq 3 ]; then
        local REMAP="--ros-args -r /tf:=/$3/tf -r /tf_static:=/$3/tf_static"
    else
        local REMAP=""
    fi
    local CMD="ros2 run tf2_ros tf2_echo $1 $2 $REMAP"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "tf_echo $*"
    print -s -- "$CMD"
}

# Colcon

function cb {
    CMD="colcon build --symlink-install"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "cb $*"
    print -s -- "$CMD"
}

function cbp {
    if [ $# -eq 0 ]; then
        PACKAGE=$(colcon list -n | fzf)
        [[ -z "$PACKAGE" ]] && return
        local CMD="colcon build --symlink-install --packages-select $PACKAGE"
    else
        local CMD="colcon build --symlink-install --packages-select $@"
    fi
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "cbp $*"
    print -s -- "$CMD"
}

function cl {
    CMD="colcon list -n"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "cl $*"
    print -s -- "$CMD"
}

# Rosdep

function rosdep_install {
    local CMD="rosdep install --from-paths src --ignore-src -r -y"
    cyan "$CMD"
    _ros2_run_cmd "$CMD"
    print -s -- "rosdep_install"
    print -s -- "$CMD"
}
