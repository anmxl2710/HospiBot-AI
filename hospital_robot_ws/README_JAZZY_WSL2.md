# ROS 2 Jazzy (WSL2) – run the hospital Gazebo demo

This repo is set up like a ROS 2 workspace (`hospital_robot_ws/`) containing:
- `hospital_world` (Gazebo world + models)
- `hospital_task_manager` (task auction + demo client)
- `hospital_fleet_manager` (per-robot executor that drives robots live)
- `fleet_interfaces` (messages)

## Important note about Jazzy + Gazebo (and why Humble is easier)

ROS 2 **Jazzy** on Ubuntu 24.04 typically uses **Gazebo Harmonic** (`gz sim`) via the `ros_gz` stack.
This codebase currently uses **Gazebo Classic** integration (`gazebo_ros`, `libgazebo_ros_diff_drive.so`).

That means you have **two ways** to run the demo:

### Option A (recommended): run the demo on Humble with Gazebo Classic

If your goal is “get a live simulation running ASAP”, use **ROS 2 Humble on Ubuntu 22.04**.
See `README_HUMBLE_WSL2.md`.

### Option B (stay on Jazzy): run with Gazebo Harmonic and port the plugins

If you must stay on Jazzy, we need to run `gz sim` and replace the Classic diff-drive plugin
(`libgazebo_ros_diff_drive.so`) with Gazebo Harmonic systems + ROS bridging (`ros_gz_bridge`).

This repo already has a **demo launch** and **world** ready (`hospital_demo.launch.py` and `hospital_demo.world`);
the remaining work for Option B is the Gazebo-Harmonic plugin/bridge wiring.

## WSL2 setup (Ubuntu 24.04)

1. Install WSL2 + Ubuntu 24.04.
2. Inside Ubuntu, install ROS 2 Jazzy (desktop):
   - Follow the official Jazzy install docs for Ubuntu 24.04.
3. Install build tools:

```bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions python3-rosdep git
sudo rosdep init || true
rosdep update
```

## Build the workspace

```bash
cd ~/hospital_robot_ws
rosdep install --from-paths src -y --ignore-src
colcon build
source install/setup.bash
```

## Launch (Gazebo Classic path)

If you have Gazebo Classic + `gazebo_ros` available in your environment:

```bash
source /opt/ros/jazzy/setup.bash
source ~/hospital_robot_ws/install/setup.bash
ros2 launch hospital_task_manager hospital_demo.launch.py
```

If `gazebo_ros` / classic plugins are not available on Jazzy, you must use Option B (port to `ros_gz`).

## What you should see

- Gazebo opens with the hospital floor.
- 3 robots spawn: `cleaner`, `sample`, `hybrid`
- Demo tasks start publishing (client node), auctions run, and the winning robot **drives** to pickup/dropoff.

