#!/usr/bin/env bash
set -euo pipefail

WS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -f "/opt/ros/jazzy/setup.bash" ]; then
  source "/opt/ros/jazzy/setup.bash"
else
  echo "ERROR: /opt/ros/jazzy/setup.bash not found. Install ROS 2 Jazzy first."
  exit 1
fi

cd "$WS_ROOT"

if [ ! -d "install" ]; then
  echo "Workspace not built yet. Building..."
  rosdep install --from-paths src -y --ignore-src || true
  colcon build
fi

source "$WS_ROOT/install/setup.bash"

echo "Launching hospital demo..."
ros2 launch hospital_task_manager hospital_demo.launch.py

