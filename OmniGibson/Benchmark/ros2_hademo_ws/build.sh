#!/usr/bin/env bash
set -euo pipefail

workspace_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

set +u
source /opt/ros/humble/setup.bash
set -u
cd "$workspace_dir"
colcon build --symlink-install

echo
echo "ROS 2 workspace built successfully."
echo "Run: source $workspace_dir/install/setup.bash"
