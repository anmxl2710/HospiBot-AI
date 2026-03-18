#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_share = get_package_share_directory("hospital_robot_sim")
    world_path = os.path.join(pkg_share, "worlds", "hospital.world")

    gazebo_ros_share = get_package_share_directory("gazebo_ros")
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros_share, "launch", "gazebo.launch.py")),
        launch_arguments={"world": world_path}.items(),
    )

    urdf_white = os.path.join(pkg_share, "urdf", "robot_white.urdf")
    urdf_green = os.path.join(pkg_share, "urdf", "robot_green.urdf")
    urdf_box = os.path.join(pkg_share, "urdf", "robot_box.urdf")

    # Spawn robots after Gazebo boots
    spawn_robots = TimerAction(
        period=2.5,
        actions=[
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=["-entity", "robot_1", "-file", urdf_white, "-x", "0.0", "-y", "-4.0", "-z", "0.2"],
                output="screen",
            ),
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=["-entity", "robot_2", "-file", urdf_green, "-x", "-6.3", "-y", "-7.0", "-z", "0.2"],
                output="screen",
            ),
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=["-entity", "robot_3", "-file", urdf_box, "-x", "0.0", "-y", "0.0", "-z", "0.2"],
                output="screen",
            ),
        ],
    )

    # Robot state publishers (for RViz TF)
    rsp_1 = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="rsp_robot_1",
        parameters=[{"robot_description": open(urdf_white, "r").read()}],
        output="screen",
    )

    rsp_2 = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="rsp_robot_2",
        parameters=[{"robot_description": open(urdf_green, "r").read()}],
        output="screen",
    )

    rsp_3 = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="rsp_robot_3",
        parameters=[{"robot_description": open(urdf_box, "r").read()}],
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
        parameters=[{"robot_id": "robot_2", "idle_x": -6.3, "idle_y": -7.0, "initial_status": "moving"}],
        output="screen",
    )
    ctrl_3 = Node(
        package="hospital_robot_sim",
        executable="robot_controller_node.py",
        name="robot_3_controller",
        parameters=[{"robot_id": "robot_3", "idle_x": 0.0, "idle_y": 0.0, "initial_status": "at_task"}],
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
            gazebo,
            spawn_robots,
            task_manager,
            auction,
            ctrl_1,
            ctrl_2,
            ctrl_3,
            rviz,
            # Optional TF publishers; safe even if TF isn't used
            rsp_1,
            rsp_2,
            rsp_3,
        ]
    )

