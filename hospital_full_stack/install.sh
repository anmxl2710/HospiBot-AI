#!/bin/bash
# ============================================================
# Hospital Full Stack - Install Script
# ============================================================
# Run from the folder where you extracted the zip:
#   chmod +x install.sh
#   ./install.sh
# ============================================================

set -e
WS=~/hospital_robot_ws

echo ""
echo "============================================================"
echo " HOSPITAL MULTI-ROBOT SYSTEM - INSTALLER"
echo "============================================================"

# Source ROS2
source /opt/ros/humble/setup.bash

# ── Step 1: Copy new packages into your existing workspace ───
echo ""
echo "[1/4] Copying packages into $WS/src ..."

cp -r src/fleet_interfaces         $WS/src/
cp -r src/hospital_task_manager    $WS/src/
cp -r src/hospital_fleet_manager   $WS/src/

# ── Step 2: Upgrade robot SDFs (add wheels + plugins) ───────
echo "[2/4] Upgrading robot SDF models..."
cp src/hospital_world/robots/cleaner_robot/model.sdf \
   $WS/src/hospital_world/robots/cleaner_robot/model.sdf
cp src/hospital_world/robots/sample_robot/model.sdf  \
   $WS/src/hospital_world/robots/sample_robot/model.sdf
cp src/hospital_world/robots/hybrid_robot/model.sdf  \
   $WS/src/hospital_world/robots/hybrid_robot/model.sdf

# Update CMakeLists to install robot models
cp src/hospital_world/CMakeLists.txt \
   $WS/src/hospital_world/CMakeLists.txt

echo "Files copied."

# ── Step 3: Build ────────────────────────────────────────────
echo ""
echo "[3/4] Building workspace (takes ~2 min)..."
cd $WS
colcon build --symlink-install

# ── Step 4: Source ───────────────────────────────────────────
echo ""
echo "[4/4] Sourcing workspace..."
source $WS/install/setup.bash

# Add to bashrc if not already there
grep -q "hospital_robot_ws/install/setup.bash" ~/.bashrc || \
  echo "source $WS/install/setup.bash" >> ~/.bashrc

echo ""
echo "============================================================"
echo " INSTALL COMPLETE!"
echo "============================================================"
echo ""
echo "STEP 1 — Open Gazebo with your hospital world:"
echo "  gazebo ~/hospital_robot_ws/src/hospital_world/worlds/hospital.world"
echo ""
echo "STEP 2 — In a NEW terminal, launch the ROS2 system:"
echo "  source ~/hospital_robot_ws/install/setup.bash"
echo "  ros2 launch hospital_task_manager hospital_system.launch.py"
echo ""
echo "STEP 3 — Watch it work! Monitor in another terminal:"
echo "  ros2 topic echo /hospital/assignment"
echo ""
echo "STEP 4 — Send a manual task anytime:"
echo "  ros2 topic pub --once /hospital/new_task fleet_interfaces/msg/Task \\"
echo "    \"{task_id: 'test1', task_type: 'deliver_sample', \\"
echo "      pickup_location: 'patient_room_1', dropoff_location: 'lab', \\"
echo "      priority: 3, pickup_x: -8.257, pickup_y: -5.543, \\"
echo "      dropoff_x: 4.219, dropoff_y: 9.199, status: 'pending'}\""
echo ""
