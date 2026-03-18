# Hospital Robot Workspace

This workspace contains multiple ROS 2 packages. The package that matches the requested
hospital Gazebo simulation is:

- `hospital_robot_sim` (ROS 2 Humble + Gazebo Classic 11)

## Quick start (WSL2 Ubuntu 22.04 + ROS 2 Humble)

```bash
source /opt/ros/humble/setup.bash
cd ~/hospital_robot_ws
rosdep install --from-paths src -y --ignore-src
colcon build
source install/setup.bash
ros2 launch hospital_robot_sim hospital_sim.launch.py
```

See `src/hospital_robot_sim/README.md` for details.

