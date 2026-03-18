# ROS 2 Jazzy (WSL2) – run the hospital Gazebo demo

This repo is set up like a ROS 2 workspace (`hospital_robot_ws/`) containing multiple packages.

For **Jazzy + Gazebo Harmonic**, use:
- `hospital_robot_sim` (world + Gazebo Harmonic models + ros_gz bridge + demo nodes)

## Jazzy + Gazebo Harmonic (supported)

ROS 2 **Jazzy** on Ubuntu 24.04 uses **Gazebo Harmonic** (`gz sim`) via the `ros_gz` stack.
This repo now includes a Jazzy/Harmonic-compatible launch that:

- starts `gz sim` with `worlds/hospital_jazzy.sdf`
- spawns 3 robots (SDF models with DiffDrive + LiDAR systems)
- bridges `/robot_X/cmd_vel`, `/robot_X/odom`, `/robot_X/scan` with `ros_gz_bridge`
- runs the demo loop (task manager → auction → robot controllers)
- opens RViz

## WSL2 setup (Ubuntu 24.04)

1. Install WSL2 + Ubuntu 24.04.
2. Inside Ubuntu, install ROS 2 Jazzy (desktop) using the official Jazzy docs.
3. Install Gazebo Harmonic integration + bridge:

```bash
sudo apt update
sudo apt install -y ros-jazzy-ros-gz ros-jazzy-ros-gz-bridge
```

4. Install build tools:

```bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions python3-rosdep git
sudo rosdep init || true
rosdep update
```

## Build the workspace

```bash
source /opt/ros/jazzy/setup.bash
cd ~/hospital_robot_ws
rosdep install --from-paths src -y --ignore-src
colcon build
source install/setup.bash
```

## Launch (Jazzy + Gazebo Harmonic path)

```bash
source /opt/ros/jazzy/setup.bash
source ~/hospital_robot_ws/install/setup.bash
ros2 launch hospital_robot_sim hospital_sim_jazzy.launch.py
```

## What you should see

- `gz sim` opens with the hospital floor (outer walls, corridors, rooms, markers).
- 3 robots spawn: `robot_1` (white sphere), `robot_2` (green sphere), `robot_3` (green box)
- Demo tasks publish every ~15s; auction runs; winning robot drives to the task and returns.

