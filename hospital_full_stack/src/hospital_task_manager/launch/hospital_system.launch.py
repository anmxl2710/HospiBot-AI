#!/usr/bin/env python3
"""
Hospital System Launch File
============================
Starts the full hospital multi-robot task management system.

Robot positions from your hospital.world:
  cleaner_1 → (4.219,  9.199)   namespace: /cleaner
  cleaner_2 → (-4.123, 9.139)   namespace: /cleaner2   (second cleaner)
  hybrid    → (-6.743, 6.098)   namespace: /hybrid

Usage:
  ros2 launch hospital_task_manager hospital_system.launch.py

Then open Gazebo separately with your existing world:
  cd ~/hospital_robot_ws/src/hospital_world/worlds
  gazebo hospital.world
"""

from launch import LaunchDescription
from launch.actions import TimerAction, ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():

    # ── Task Manager (auctioneer) ──────────────────────────────
    task_manager = Node(
        package='hospital_task_manager',
        executable='task_manager',
        name='task_manager',
        output='screen',
    )

    # ── Fleet Manager: cleaner (robot 1 at 4.219, 9.199) ──────
    fleet_cleaner = Node(
        package='hospital_fleet_manager',
        executable='fleet_manager',
        name='fleet_cleaner',
        parameters=[{
            'robot_id':   'cleaner',
            'robot_type': 'cleaner',
            'start_x':    4.219,
            'start_y':    9.199,
        }],
        output='screen',
    )

    # ── Fleet Manager: sample robot ────────────────────────────
    # (using cleaner_robot_2 as sample robot at -4.123, 9.139)
    fleet_sample = Node(
        package='hospital_fleet_manager',
        executable='fleet_manager',
        name='fleet_sample',
        parameters=[{
            'robot_id':   'sample',
            'robot_type': 'sample',
            'start_x':    -4.123,
            'start_y':     9.139,
        }],
        output='screen',
    )

    # ── Fleet Manager: hybrid robot at (-6.743, 6.098) ────────
    fleet_hybrid = Node(
        package='hospital_fleet_manager',
        executable='fleet_manager',
        name='fleet_hybrid',
        parameters=[{
            'robot_id':   'hybrid',
            'robot_type': 'hybrid',
            'start_x':    -6.743,
            'start_y':     6.098,
        }],
        output='screen',
    )

    # ── Client node (sends demo tasks, delayed 5s) ─────────────
    client = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='hospital_task_manager',
                executable='client_node',
                name='hospital_client',
                output='screen',
            )
        ]
    )

    return LaunchDescription([
        task_manager,
        fleet_cleaner,
        fleet_sample,
        fleet_hybrid,
        client,
    ])
