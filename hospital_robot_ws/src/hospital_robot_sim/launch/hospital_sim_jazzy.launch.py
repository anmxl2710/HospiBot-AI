#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_share = get_package_share_directory("hospital_robot_sim")

    world_path = os.path.join(pkg_share, "worlds", "hospital_jazzy.sdf")

    # Start Gazebo Harmonic
    ros_gz_share = get_package_share_directory("ros_gz_sim")
    gz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_share, "launch", "gz_sim.launch.py")),
        launch_arguments={"gz_args": f"-r -v 3 {world_path}"}.items(),
    )

    # Make sure Gazebo can find our local models
    gz_model_path = os.path.join(pkg_share, "models")

    # Spawn models into Gazebo
    spawn = TimerAction(
        period=2.5,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                arguments=[
                    "-name", "robot_1",
                    "-file", os.path.join(gz_model_path, "robot_white", "model.sdf"),
                    "-x", "0.0", "-y", "-4.0", "-z", "0.2",
                ],
                output="screen",
            ),
            Node(
                package="ros_gz_sim",
                executable="create",
                arguments=[
                    "-name", "robot_2",
                    "-file", os.path.join(gz_model_path, "robot_green", "model.sdf"),
                    "-x", "-6.3", "-y", "-7.0", "-z", "0.2",
                ],
                output="screen",
            ),
            Node(
                package="ros_gz_sim",
                executable="create",
                arguments=[
                    "-name", "robot_3",
                    "-file", os.path.join(gz_model_path, "robot_box", "model.sdf"),
                    "-x", "0.0", "-y", "0.0", "-z", "0.2",
                ],
                output="screen",
            ),
        ],
    )

    # Bridge cmd_vel/odom/scan between ROS and Gazebo
    bridge_cfg = os.path.join(pkg_share, "config", "ros_gz_bridge.yaml")
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[bridge_cfg],
        output="screen",
    )

    task_manager = Node(
        package="hospital_robot_sim",
        executable="task_manager_node.py",
        name="task_manager_node",
        parameters=[{"period_s": 15.0}],
        output="screen",
    )

    auction = Node(
        package="hospital_robot_sim",
        executable="auction_node.py",
        name="auction_node",
        parameters=[{"battery_weight": 2.5}],
        output="screen",
    )

    ctrl_1 = Node(
        package="hospital_robot_sim",
        executable="robot_controller_node.py",
        name="robot_1_controller",
        parameters=[{"robot_id": "robot_1", "idle_x": 0.0, "idle_y": -4.0, "initial_status": "idle"}],
        output="screen",
    )
    ctrl_2 = Node(
        package="hospital_robot_sim",
        executable="robot_controller_node.py",
        name="robot_2_controller",
        parameters=[{"robot_id": "robot_2", "idle_x": -6.3, "idle_y": -7.0, "initial_status": "idle"}],
        output="screen",
    )
    ctrl_3 = Node(
        package="hospital_robot_sim",
        executable="robot_controller_node.py",
        name="robot_3_controller",
        parameters=[{"robot_id": "robot_3", "idle_x": 0.0, "idle_y": 0.0, "initial_status": "idle"}],
        output="screen",
    )

    rviz_cfg = os.path.join(pkg_share, "rviz", "hospital.rviz")
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_cfg],
        output="screen",
    )

    return LaunchDescription(
        [
            gz_launch,
            spawn,
            bridge,
            task_manager,
            auction,
            ctrl_1,
            ctrl_2,
            ctrl_3,
            rviz,
        ]
    )

