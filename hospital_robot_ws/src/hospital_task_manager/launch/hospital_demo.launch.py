#!/usr/bin/env python3
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    hospital_world_share = get_package_share_directory('hospital_world')
    world_path = os.path.join(hospital_world_share, 'worlds', 'hospital_demo.world')

    gazebo_ros_share = get_package_share_directory('gazebo_ros')
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_share, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_path}.items(),
    )

    # Spawn robots (after Gazebo boots)
    spawner = TimerAction(
        period=3.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(hospital_world_share, 'launch', 'spawn_hospital_robots.launch.py')
                )
            )
        ],
    )

    task_manager = Node(
        package='hospital_task_manager',
        executable='task_manager',
        name='task_manager',
        output='screen',
    )

    fleet_cleaner = Node(
        package='hospital_fleet_manager',
        executable='fleet_manager',
        name='fleet_cleaner',
        parameters=[{
            'robot_id': 'cleaner',
            'robot_type': 'cleaner',
            'start_x': 4.219,
            'start_y': 9.199,
        }],
        output='screen',
    )

    fleet_sample = Node(
        package='hospital_fleet_manager',
        executable='fleet_manager',
        name='fleet_sample',
        parameters=[{
            'robot_id': 'sample',
            'robot_type': 'sample',
            'start_x': -4.123,
            'start_y': 9.139,
        }],
        output='screen',
    )

    fleet_hybrid = Node(
        package='hospital_fleet_manager',
        executable='fleet_manager',
        name='fleet_hybrid',
        parameters=[{
            'robot_id': 'hybrid',
            'robot_type': 'hybrid',
            'start_x': -6.743,
            'start_y': 6.098,
        }],
        output='screen',
    )

    client = TimerAction(
        period=8.0,
        actions=[
            Node(
                package='hospital_task_manager',
                executable='client_node',
                name='hospital_client',
                output='screen',
            )
        ],
    )

    return LaunchDescription([
        gazebo_launch,
        spawner,
        task_manager,
        fleet_cleaner,
        fleet_sample,
        fleet_hybrid,
        client,
    ])

