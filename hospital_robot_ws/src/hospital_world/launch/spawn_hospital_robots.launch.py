from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    robots = []

    robot_positions = [
        ("cleaner", 4.219, 9.199, "cleaner_robot"),
        ("sample", -4.123, 9.139, "sample_robot"),
        ("hybrid", -6.743, 6.098, "hybrid_robot"),
        
    ]

    pkg_share = get_package_share_directory("hospital_world")

    for robot_id, x, y, model_name in robot_positions:
        model_path = os.path.join(pkg_share, "models", model_name, "model.sdf")
        robots.append(
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=[
                    "-entity", robot_id,
                    "-file", model_path,
                    "-x", str(x),
                    "-y", str(y),
                    "-z", "0.1"
                ],
                output="screen"
            )
        )

    return LaunchDescription(robots)
