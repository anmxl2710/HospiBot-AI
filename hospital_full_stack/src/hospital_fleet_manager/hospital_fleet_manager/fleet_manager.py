#!/usr/bin/env python3
"""
Hospital Fleet Manager Node
============================
One instance runs per robot. Handles bidding and task execution.

Launch one per robot:
  ros2 run hospital_fleet_manager fleet_manager \
    --ros-args -p robot_id:=cleaner -p robot_type:=cleaner \
               -p start_x:=4.22 -p start_y:=9.20

Robot namespaces (must match SDF plugins):
  cleaner → /cleaner/cmd_vel, /cleaner/odom, /cleaner/scan
  sample  → /sample/cmd_vel,  /sample/odom,  /sample/scan
  hybrid  → /hybrid/cmd_vel,  /hybrid/odom,  /hybrid/scan
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import math
import time
import threading

from fleet_interfaces.msg import Task, Bid, Assignment
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import String


# Robot capabilities map
CAPABILITIES = {
    'cleaner': ['clean'],
    'sample':  ['deliver_sample'],
    'hybrid':  ['clean', 'deliver_sample', 'deliver_medicine', 'hybrid'],
}

# Approximate task execution durations (seconds)
TASK_DURATION = {
    'clean':            20.0,
    'deliver_sample':    8.0,
    'deliver_medicine':  8.0,
    'hybrid':           25.0,
}

ROBOT_SPEED      = 0.4   # m/s (conservative for hospital corridors)
MIN_ENERGY       = 20.0  # % — won't bid below this
ENERGY_PER_METER = 0.15  # % battery drain per meter


class State:
    IDLE       = 'idle'
    BUSY       = 'busy'
    CHARGING   = 'charging'


class FleetManager(Node):

    def __init__(self):
        super().__init__('fleet_manager')

        # Parameters
        self.declare_parameter('robot_id',   'cleaner')
        self.declare_parameter('robot_type', 'cleaner')
        self.declare_parameter('start_x',    0.0)
        self.declare_parameter('start_y',    0.0)

        self.robot_id   = self.get_parameter('robot_id').value
        self.robot_type = self.get_parameter('robot_type').value
        self.pos_x      = self.get_parameter('start_x').value
        self.pos_y      = self.get_parameter('start_y').value
        self.caps       = CAPABILITIES.get(self.robot_type, [])
        self.energy     = 100.0
        self.state      = State.IDLE
        self.cur_task   = None

        ns = f'/{self.robot_id}'   # e.g. /cleaner

        self.get_logger().info(
            f'\n{"="*45}\n'
            f' Fleet Manager: {self.robot_id} ({self.robot_type})\n'
            f' Capabilities : {self.caps}\n'
            f' Namespace    : {ns}\n'
            f' Start pos    : ({self.pos_x}, {self.pos_y})\n'
            f'{"="*45}'
        )

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Publishers
        self.bid_pub    = self.create_publisher(Bid,    '/hospital/bid',  qos)
        self.status_pub = self.create_publisher(String, f'{ns}/fleet_status', 10)
        self.cmd_pub    = self.create_publisher(Twist,  f'{ns}/cmd_vel',  10)
        self.goal_pub   = self.create_publisher(PoseStamped, f'{ns}/goal_pose', 10)

        # Subscribers
        self.create_subscription(Task,       '/hospital/bid_request', self._on_bid_req,    qos)
        self.create_subscription(Assignment, '/hospital/assignment',  self._on_assignment,  qos)
        self.create_subscription(Odometry,   f'{ns}/odom',            self._on_odom,        10)

        # Periodic status
        self.create_timer(3.0, self._pub_status)

        self.get_logger().info(f'{self.robot_id} ready and listening for tasks.')

    # ----------------------------------------------------------
    # BID REQUEST
    # ----------------------------------------------------------
    def _on_bid_req(self, task: Task):
        if self.state != State.IDLE:
            self.get_logger().info(
                f'[{self.robot_id}] Skipping bid — state={self.state}')
            return

        capable = task.task_type in self.caps
        dist    = self._dist(self.pos_x, self.pos_y, task.pickup_x, task.pickup_y)
        travel  = dist / ROBOT_SPEED
        dur     = TASK_DURATION.get(task.task_type, 10.0)
        eta     = travel + dur

        # Weighted cost (matches TaskManager formula)
        energy_penalty = max(0.0, (100.0 - self.energy) / 100.0)
        cost = 0.5 * eta + 0.3 * dist + 0.2 * energy_penalty * 100.0

        bid = Bid()
        bid.task_id      = task.task_id
        bid.robot_id     = self.robot_id
        bid.robot_type   = self.robot_type
        bid.eta          = eta
        bid.cost         = cost
        bid.energy_level = self.energy
        bid.distance     = dist
        bid.can_do_task  = capable and (self.energy > MIN_ENERGY)

        self.bid_pub.publish(bid)
        self.get_logger().info(
            f'[{self.robot_id}] BID sent | task={task.task_id} | '
            f'ETA={eta:.1f}s | Dist={dist:.1f}m | '
            f'CanDo={bid.can_do_task}'
        )

    # ----------------------------------------------------------
    # ASSIGNMENT
    # ----------------------------------------------------------
    def _on_assignment(self, msg: Assignment):
        if msg.winner_robot_id == self.robot_id:
            self.get_logger().info(
                f'\n[{self.robot_id}] *** WON TASK {msg.task_id} ***\n'
                f'  ETA={msg.eta:.1f}s'
            )
            self.state    = State.BUSY
            self.cur_task = msg.task_id
            # Execute task in background thread (non-blocking)
            threading.Thread(
                target=self._execute_task,
                args=(msg,),
                daemon=True
            ).start()
        elif self.robot_id in msg.losing_robot_ids:
            self.get_logger().info(
                f'[{self.robot_id}] Lost auction for {msg.task_id} '
                f'(winner: {msg.winner_robot_id})'
            )

    # ----------------------------------------------------------
    # TASK EXECUTION
    # ----------------------------------------------------------
    def _execute_task(self, assignment: Assignment):
        """
        Full task lifecycle:
          navigate to pickup → execute → navigate to dropoff → idle
        """
        tid = assignment.task_id
        self.get_logger().info(f'[{self.robot_id}] Executing task {tid}...')

        # --- Phase 1: Navigate to pickup ---
        # (In a real Nav2 system, send goal_pose and wait for result)
        # Here we simulate by sleeping proportional to distance
        # and publishing a goal_pose for RViz visualization
        self._pub_goal(assignment.eta * 0.5, 0.0)   # approx pickup
        sim_travel = min(assignment.eta * 0.4, 15.0)
        self.get_logger().info(
            f'[{self.robot_id}] Navigating to pickup (~{sim_travel:.0f}s)...')
        time.sleep(sim_travel)

        # Drain battery
        self.energy = max(0.0, self.energy - sim_travel * ROBOT_SPEED * ENERGY_PER_METER)

        # --- Phase 2: Execute task at pickup ---
        task_type = assignment.robot_type   # reuse field for task type
        dur = TASK_DURATION.get('deliver_sample', 8.0)
        self.get_logger().info(
            f'[{self.robot_id}] Performing task at pickup ({dur:.0f}s)...')
        time.sleep(dur)

        # --- Phase 3: Navigate to dropoff ---
        self.get_logger().info(
            f'[{self.robot_id}] Navigating to dropoff...')
        time.sleep(sim_travel)
        self.energy = max(0.0, self.energy - sim_travel * ROBOT_SPEED * ENERGY_PER_METER)

        # --- Done ---
        self.get_logger().info(
            f'[{self.robot_id}] ✓ Task {tid} COMPLETE | '
            f'Energy: {self.energy:.0f}%'
        )
        self.cur_task = None

        if self.energy < MIN_ENERGY:
            self.get_logger().warn(
                f'[{self.robot_id}] LOW BATTERY ({self.energy:.0f}%) → CHARGING')
            self.state = State.CHARGING
            time.sleep(10.0)       # simulate charging
            self.energy = 100.0
            self.get_logger().info(f'[{self.robot_id}] Battery full → IDLE')

        self.state = State.IDLE

    # ----------------------------------------------------------
    # ODOMETRY
    # ----------------------------------------------------------
    def _on_odom(self, msg: Odometry):
        self.pos_x = msg.pose.pose.position.x
        self.pos_y = msg.pose.pose.position.y

    # ----------------------------------------------------------
    # UTILS
    # ----------------------------------------------------------
    def _dist(self, x1, y1, x2, y2) -> float:
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def _pub_goal(self, x: float, y: float):
        """Publish goal_pose for RViz visualization."""
        g = PoseStamped()
        g.header.frame_id = 'map'
        g.header.stamp = self.get_clock().now().to_msg()
        g.pose.position.x = x
        g.pose.position.y = y
        g.pose.orientation.w = 1.0
        self.goal_pub.publish(g)

    def _pub_status(self):
        s = String()
        s.data = (
            f'[{self.robot_id}] state={self.state} | '
            f'energy={self.energy:.0f}% | '
            f'pos=({self.pos_x:.1f},{self.pos_y:.1f})'
        )
        self.status_pub.publish(s)


def main(args=None):
    rclpy.init(args=args)
    node = FleetManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
