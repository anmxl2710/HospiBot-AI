#!/usr/bin/env python3

import random
import uuid

import rclpy
from rclpy.node import Node

from hospital_robot_sim.msg import Task


TASK_TYPES = [
    "lab_pickup",
    "medicine_delivery",
    "patient_transport",
    "cleaning",
]

# Marker locations matching the world file
TASK_MARKERS = [
    ("pickup_left", -10.5, 0.8),
    ("dropoff_right", 10.5, 0.8),
]


class TaskManagerNode(Node):
    """
    Publishes new tasks periodically for the demo.
    Topic: /tasks (hospital_robot_sim/Task)
    """

    def __init__(self):
        super().__init__("task_manager_node")
        self.pub = self.create_publisher(Task, "/tasks", 10)

        self.declare_parameter("period_s", 15.0)
        self.period_s = float(self.get_parameter("period_s").value)

        self.get_logger().info(
            f"Task manager online. Publishing demo tasks every {self.period_s:.0f}s."
        )
        self.create_timer(self.period_s, self._publish_task)

    def _publish_task(self):
        task = Task()
        task.task_id = f"T_{str(uuid.uuid4())[:8]}"
        task.task_type = random.choice(TASK_TYPES)

        marker_id, x, y = random.choice(TASK_MARKERS)
        task.marker_id = marker_id
        task.target_x = float(x)
        task.target_y = float(y)

        self.pub.publish(task)
        self.get_logger().info(
            f"[TASK] {task.task_id} type={task.task_type} marker={task.marker_id} "
            f"xy=({task.target_x:.2f},{task.target_y:.2f})"
        )


def main():
    rclpy.init()
    node = TaskManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

