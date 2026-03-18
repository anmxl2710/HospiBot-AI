#!/usr/bin/env python3

import math
import time
from dataclasses import dataclass
from typing import Dict

import rclpy
from rclpy.node import Node

from hospital_robot_sim.msg import Task, TaskAssignment, AuctionResult, RobotStatus


ROBOT_IDS = ["robot_1", "robot_2", "robot_3"]


@dataclass
class RobotState:
    x: float = 0.0
    y: float = 0.0
    battery: float = 100.0
    status: str = "idle"


class AuctionNode(Node):
    """
    Sub: /tasks (Task), /robot_status (RobotStatus)
    Pub: /task_assignments (TaskAssignment), /auction_results (AuctionResult)

    Bid model:
      bid = distance_to_task + battery_cost
      battery_cost = (100 - battery)/100 * weight
    """

    def __init__(self):
        super().__init__("auction_node")

        self.declare_parameter("battery_weight", 2.5)
        self.battery_weight = float(self.get_parameter("battery_weight").value)

        self.states: Dict[str, RobotState] = {rid: RobotState() for rid in ROBOT_IDS}
        self.last_task_id = None

        self.create_subscription(Task, "/tasks", self._on_task, 10)
        self.create_subscription(RobotStatus, "/robot_status", self._on_status, 20)

        self.assignment_pub = self.create_publisher(TaskAssignment, "/task_assignments", 10)
        self.results_pub = self.create_publisher(AuctionResult, "/auction_results", 10)

        self.get_logger().info("Auction node online.")

    def _on_status(self, msg: RobotStatus):
        st = self.states.get(msg.robot_id)
        if st is None:
            self.states[msg.robot_id] = RobotState(msg.x, msg.y, msg.battery, msg.status)
        else:
            st.x = msg.x
            st.y = msg.y
            st.battery = msg.battery
            st.status = msg.status

    def _bid(self, rid: str, task: Task) -> float:
        st = self.states[rid]
        dist = math.hypot(task.target_x - st.x, task.target_y - st.y)
        battery_cost = ((100.0 - st.battery) / 100.0) * self.battery_weight
        return dist + battery_cost

    def _on_task(self, task: Task):
        # Avoid re-auctioning the same task if the publisher repeats due to timers.
        if task.task_id == self.last_task_id:
            return
        self.last_task_id = task.task_id

        eligible = [rid for rid in ROBOT_IDS if self.states[rid].status == "idle"]
        if not eligible:
            self.get_logger().warn(f"[AUCTION] No idle robots for {task.task_id}; skipping.")
            return

        bids = [(self._bid(rid, task), rid) for rid in eligible]
        bids.sort(key=lambda t: t[0])
        winning_cost, winner = bids[0]

        # Publish result
        res = AuctionResult()
        res.task_id = task.task_id
        res.winner_robot_id = winner
        res.winning_cost = float(winning_cost)
        res.bidders = [rid for _, rid in bids]
        res.costs = [float(cost) for cost, _ in bids]
        self.results_pub.publish(res)

        # Publish assignment
        assign = TaskAssignment()
        assign.task_id = task.task_id
        assign.task_type = task.task_type
        assign.robot_id = winner
        assign.target_x = task.target_x
        assign.target_y = task.target_y
        assign.bid_cost = float(winning_cost)
        self.assignment_pub.publish(assign)

        self.get_logger().info(
            f"Task assigned to {winner} | Bid: {winning_cost:.2f} (distance+battery) "
            f"| task={task.task_type} xy=({task.target_x:.2f},{task.target_y:.2f})"
        )


def main():
    rclpy.init()
    node = AuctionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

