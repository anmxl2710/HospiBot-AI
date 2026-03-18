# ROS 2 Humble (WSL2) – run the live hospital Gazebo demo

This workspace is already built around **Gazebo Classic** (`gazebo_ros` + `libgazebo_ros_diff_drive.so`).
That matches **ROS 2 Humble on Ubuntu 22.04** very well.

## 1) Use WSL2 + Ubuntu 22.04

On Windows, install WSL2 and an Ubuntu 22.04 distribution.

## 2) Install ROS 2 Humble (Desktop)

Inside Ubuntu 22.04, install ROS 2 Humble Desktop using the official docs.

After install, you should have:
- `/opt/ros/humble/setup.bash`
- `ros2` in PATH

## 3) Install build tooling

```bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions python3-rosdep
sudo rosdep init || true
rosdep update
```

## 4) Put the workspace in your WSL home (recommended)

In WSL:

```bash
mkdir -p ~/hospital_robot_ws
```

Copy the folder `hospital_robot_ws/` from Windows into `~/hospital_robot_ws/` (WSL filesystem).
Avoid building from `/mnt/c/...` (it’s slower and can cause path/permission weirdness).

## 5) Build

```bash
source /opt/ros/humble/setup.bash
cd ~/hospital_robot_ws
rosdep install --from-paths src -y --ignore-src
colcon build
source install/setup.bash
```

## 6) Run the live demo (Gazebo opens + robots move)

```bash
source /opt/ros/humble/setup.bash
source ~/hospital_robot_ws/install/setup.bash
ros2 launch hospital_task_manager hospital_demo.launch.py
```

## What you should see

- Gazebo opens with the hospital floor (`hospital_demo.world`)
- 3 robots spawn: `cleaner`, `sample`, `hybrid`
- Demo tasks are published; auctions run; the winning robot **drives** to pickup/dropoff coordinates

## If something fails

Paste the terminal output and I’ll patch the launch/model files to match your environment.

