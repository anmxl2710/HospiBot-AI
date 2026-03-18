# Hospital Robot Simulation (ROS 2 Humble + Gazebo Classic 11)

This package creates a **hospital floor Gazebo world** and spawns **3 autonomous mobile robots**.
It also runs a demo loop:

- every ~15s a task appears at a pink marker
- an auction picks the best idle robot (distance + battery cost)
- the winner drives to the marker, pauses 3s, then returns to its idle spot

## Requirements

- Ubuntu 22.04 (recommended via **WSL2** on Windows)
- ROS 2 **Humble**
- Gazebo Classic **11** (installed with ROS desktop on Humble)
- Python 3.10+

## Setup (WSL2 Ubuntu 22.04)

1) Install ROS 2 Humble Desktop and source it:

```bash
source /opt/ros/humble/setup.bash
```

2) Install build tools:

```bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions python3-rosdep
sudo rosdep init || true
rosdep update
```

3) Build this workspace:

```bash
cd ~/hospital_robot_ws
rosdep install --from-paths src -y --ignore-src
colcon build
source install/setup.bash
```

## Run

```bash
source /opt/ros/humble/setup.bash
source ~/hospital_robot_ws/install/setup.bash
ros2 launch hospital_robot_sim hospital_sim.launch.py
```

## What you will see

- **Gazebo** opens with the hospital layout (grey grid tiles, brown outer walls, rooms, corridors, beds)
- 3 robots spawn:
  - `robot_1` white sphere (lower corridor, idle)
  - `robot_2` green sphere (patient rooms, moving in demo)
  - `robot_3` green box (middle zone, at-task initially)
- pink task markers are in the middle zone
- a blue path line is drawn in Gazebo as static segments (demo visualization)
- terminal prints: `Task assigned to robot_X | Bid: Y ...`

## Topics

- **Tasks**: `/tasks` (`hospital_robot_sim/Task`)
- **Assignments**: `/task_assignments` (`hospital_robot_sim/TaskAssignment`)
- **Auction results**: `/auction_results` (`hospital_robot_sim/AuctionResult`)
- **Robot status**: `/robot_status` (`hospital_robot_sim/RobotStatus`)
- **Robot control**: `/robot_X/cmd_vel`
- **Robot odom**: `/robot_X/odom`
- **Robot laser**: `/robot_X/scan`

## Notes

- This demo uses a **simple waypoint controller** (not full Nav2) to keep it runnable out-of-the-box.
- `config/nav2_params.yaml` is included so you can upgrade to Nav2 later.

