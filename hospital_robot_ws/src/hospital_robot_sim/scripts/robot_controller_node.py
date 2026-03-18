#!/usr/bin/env python3

import math
import time
from typing import Optional

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

from hospital_robot_sim.msg import TaskAssignment, RobotStatus


def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def norm_angle(a: float) -> float:
    while a > math.pi:
        a -= 2.0 * math.pi
    while a < -math.pi:
        a += 2.0 * math.pi
    return a


class RobotController(Node):
    """
    One instance per robot.

    Sub: /task_assignments (TaskAssignment)
    Pub: /robot_status (RobotStatus), /robot_X/cmd_vel (Twist)
    Sub: /robot_X/odom (Odometry)

    Movement: simple proportional controller to target waypoint, then return to idle pose.
    Battery: starts at 100%, drains while moving.
    """

    def __init__(self):
        super().__init__("robot_controller_node")

        self.declare_parameter("robot_id", "robot_1")
        self.declare_parameter("idle_x", 0.0)
        self.declare_parameter("idle_y", 0.0)
        self.declare_parameter("initial_status", "idle")

        self.robot_id = str(self.get_parameter("robot_id").value)
        self.idle_x = float(self.get_parameter("idle_x").value)
        self.idle_y = float(self.get_parameter("idle_y").value)
        initial_status = str(self.get_parameter("initial_status").value)

        ns = f"/{self.robot_id}"
        self.cmd_pub = self.create_publisher(Twist, f"{ns}/cmd_vel", 10)
        self.status_pub = self.create_publisher(RobotStatus, "/robot_status", 20)

        self.create_subscription(Odometry, f"{ns}/odom", self._on_odom, 20)
        self.create_subscription(TaskAssignment, "/task_assignments", self._on_assignment, 20)

        self.x = self.idle_x
        self.y = self.idle_y
        self.yaw = 0.0

        self.battery = 100.0
        self.status = initial_status if initial_status in {"idle", "moving", "at_task", "returning"} else "idle"
        self._active_goal = None  # (x,y)
        self._active_task_id: Optional[str] = None

        self.declare_parameter("max_v", 0.35)
        self.declare_parameter("max_w", 1.2)
        self.max_v = float(self.get_parameter("max_v").value)
        self.max_w = float(self.get_parameter("max_w").value)

        self.create_timer(0.2, self._tick)  # 5 Hz
        self.create_timer(1.0, self._publish_status)

        self.get_logger().info(
            f"{self.robot_id} controller online. idle=({self.idle_x:.2f},{self.idle_y:.2f})"
        )

    def _on_odom(self, msg: Odometry):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.yaw = yaw_from_quat(q.x, q.y, q.z, q.w)

    def _on_assignment(self, msg: TaskAssignment):
        if msg.robot_id != self.robot_id:
            return
        if self.status != "idle":
            return

        self._active_task_id = msg.task_id
        self._active_goal = (float(msg.target_x), float(msg.target_y))
        self.status = "moving"
        self.get_logger().info(
            f"[{self.robot_id}] Assigned {msg.task_type} {msg.task_id} -> "
            f"({msg.target_x:.2f},{msg.target_y:.2f})"
        )

    def _drive_step(self, gx: float, gy: float) -> bool:
        dx = gx - self.x
        dy = gy - self.y
        dist = math.hypot(dx, dy)
        if dist < 0.30:
            self.cmd_pub.publish(Twist())
            return True

        target_yaw = math.atan2(dy, dx)
        err = norm_angle(target_yaw - self.yaw)

        k_ang = 1.8
        k_lin = 0.7

        cmd = Twist()
        cmd.angular.z = max(-self.max_w, min(self.max_w, k_ang * err))
        if abs(err) < 0.7:
            cmd.linear.x = max(0.0, min(self.max_v, k_lin * dist))
        else:
            cmd.linear.x = 0.0

        self.cmd_pub.publish(cmd)

        # Battery drain while moving
        self.battery = max(0.0, self.battery - (abs(cmd.linear.x) * 0.4 + abs(cmd.angular.z) * 0.05))
        return False

    def _tick(self):
        if self._active_goal is None:
            return

        gx, gy = self._active_goal
        arrived = self._drive_step(gx, gy)
        if not arrived:
            return

        # State transitions
        if self.status == "moving":
            self.status = "at_task"
            self.get_logger().info(f"[{self.robot_id}] Reached task; executing 3s...")
            time.sleep(3.0)
            self.status = "returning"
            self._active_goal = (self.idle_x, self.idle_y)
        elif self.status == "returning":
            self.status = "idle"
            self._active_goal = None
            self.get_logger().info(f"[{self.robot_id}] Returned to idle.")

    def _publish_status(self):
        msg = RobotStatus()
        msg.robot_id = self.robot_id
        msg.status = self.status
        msg.x = float(self.x)
        msg.y = float(self.y)
        msg.battery = float(self.battery)
        self.status_pub.publish(msg)


def main():
    rclpy.init()
    node = RobotController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

