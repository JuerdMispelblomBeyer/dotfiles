#!/bin/bash
set -e

###########################################################
# ROS 2 workspace autosource helper
# Assumes all exr2 workspaces are in current user's HOME
###########################################################
_ros_autosource_exr2 () {
    local root="$HOME/exr2"
    local ws                                # iterator

    # Loops in alphabetical order for deterministic overlay stack
    for ws in "$root"/*/ ; do

        # Ignore non‑directories (globbing safety)
        [[ -d $ws ]] || continue            # -d checks if it's a valid dir

        # Absolute path to this workspace’s setup file
        local setup_file="${ws%/}/install/setup.bash"

        # Only source if the workspace is *built*
        if [[ -f $setup_file ]]; then       # -f checks if it's a valid file

            # Print to console
            printf "✔  overlaying %s\n" "${ws}"

            # shellcheck disable=SC1090
            source "$setup_file"
        fi
    done
    
    #######################################################
	#   Official ROS 2 environments
	#######################################################
	for setup in \
	    /opt/ros/humble/setup.bash \
	    "$HOME/ros2_humble/install/setup.bash"
	do
		[[ -f $setup ]] && source "$setup"
	done

}
