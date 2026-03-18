#!/usr/bin/env python3
"""
Hospital Task Manager Node
===========================
Auction-based task allocation for 3 hospital robots:
  - cleaner  (namespace: /cleaner)   → cleaning tasks
  - sample   (namespace: /sample)    → sample delivery
  - hybrid   (namespace: /hybrid)    → both cleaning + delivery

Topics:
  SUB: /hospital/new_task      (fleet_interfaces/Task)
  SUB: /hospital/bid           (fleet_interfaces/Bid)
  PUB: /hospital/bid_request   (fleet_interfaces/Task)
  PUB: /hospital/assignment    (fleet_interfaces/Assignment)
  PUB: /hospital/status        (std_msgs/String)
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from threading import Timer
import uuid
import time

from fleet_interfaces.msg import Task, Bid, Assignment
from std_msgs.msg import String


class TaskManager(Node):

    BID_WINDOW = 3.0   # seconds to collect bids

    # Weighted cost: lower = better robot for this task
    W_ETA      = 0.50
    W_DISTANCE = 0.30
    W_ENERGY   = 0.20  # subtracted: prefer higher energy

    # Which robot types can handle which task types
    CAPABILITIES = {
        'cleaner': ['clean'],
        'sample':  ['deliver_sample'],
        'hybrid':  ['clean', 'deliver_sample', 'deliver_medicine', 'hybrid'],
    }

    # Room name → (x, y) coordinates matching your hospital.world
    ROOM_COORDS = {
        'patient_room_1':  (-8.25, -5.54),
        'patient_room_2':  (-8.25, -0.78),
        'patient_room_3':  (-8.25,  4.00),
        'patient_room_4':  (-8.25,  8.71),
        'corridor':        ( 0.00,  0.00),
        'lab':             ( 4.00, -5.00),
        'pharmacy':        ( 4.00,  5.00),
        'icu':             ( 4.22,  9.20),
        'charging_dock':   (-4.12,  9.14),
        'hybrid_dock':     (-6.74,  6.10),
    }

    def __init__(self):
        super().__init__('task_manager')
        self.get_logger().info('=' * 50)
        self.get_logger().info(' HOSPITAL TASK MANAGER STARTING')
        self.get_logger().info('=' * 50)

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Publishers
        self.bid_req_pub   = self.create_publisher(Task,       '/hospital/bid_request', qos)
        self.assignment_pub = self.create_publisher(Assignment, '/hospital/assignment',  qos)
        self.status_pub    = self.create_publisher(String,     '/hospital/status',       10)

        # Subscribers
        self.create_subscription(Task, '/hospital/new_task', self._on_new_task, qos)
        self.create_subscription(Bid,  '/hospital/bid',      self._on_bid,      qos)

        # State
        self.auctions = {}       # task_id → {task, bids[], start_time}
        self.assigned = {}       # task_id → robot_id
        self.queue    = []       # Tasks waiting when all robots busy

        self.get_logger().info('Task Manager ready. Waiting for tasks on /hospital/new_task')
        self._status('Task Manager online.')

    # ----------------------------------------------------------
    # NEW TASK
    # ----------------------------------------------------------
    def _on_new_task(self, task: Task):
        if not task.task_id:
            task.task_id = str(uuid.uuid4())[:8]
        task.status = 'pending'

        # Fill in coordinates if not set
        if task.pickup_x == 0.0 and task.pickup_y == 0.0:
            px, py = self.ROOM_COORDS.get(task.pickup_location, (0.0, 0.0))
            task.pickup_x, task.pickup_y = px, py
        if task.dropoff_x == 0.0 and task.dropoff_y == 0.0:
            dx, dy = self.ROOM_COORDS.get(task.dropoff_location, (0.0, 0.0))
            task.dropoff_x, task.dropoff_y = dx, dy

        pri = {1: 'LOW', 2: 'MEDIUM', 3: 'HIGH', 4: 'EMERGENCY'}.get(task.priority, '?')
        self.get_logger().info(
            f'\n[NEW TASK] {task.task_id}\n'
            f'  Type    : {task.task_type}\n'
            f'  Route   : {task.pickup_location} → {task.dropoff_location}\n'
            f'  Priority: {pri}'
        )

        self._start_auction(task)

    # ----------------------------------------------------------
    # AUCTION
    # ----------------------------------------------------------
    def _start_auction(self, task: Task):
        tid = task.task_id
        self.auctions[tid] = {
            'task': task,
            'bids': [],
            'start': time.time()
        }
        self.get_logger().info(
            f'[AUCTION] Broadcasting bid request for {tid} '
            f'(window: {self.BID_WINDOW}s)'
        )
        self.bid_req_pub.publish(task)
        self._status(f'Auction started: {tid}')

        t = Timer(self.BID_WINDOW, self._close_auction, args=[tid])
        self.auctions[tid]['timer'] = t
        t.start()

    def _on_bid(self, bid: Bid):
        tid = bid.task_id
        if tid not in self.auctions:
            return
        self.auctions[tid]['bids'].append(bid)
        self.get_logger().info(
            f'[BID] {bid.robot_id} | ETA={bid.eta:.1f}s | '
            f'Dist={bid.distance:.1f}m | Energy={bid.energy_level:.0f}% | '
            f'CanDo={bid.can_do_task}'
        )

    def _close_auction(self, tid: str):
        if tid not in self.auctions:
            return

        auction = self.auctions[tid]
        all_bids = auction['bids']
        eligible  = [b for b in all_bids if b.can_do_task]

        self.get_logger().info(
            f'[AUCTION CLOSE] {tid} | '
            f'Total={len(all_bids)} bids | Eligible={len(eligible)}'
        )

        if not eligible:
            self.get_logger().warn(
                f'[NO BIDS] No eligible robot for {tid}. Queuing...')
            self.queue.append(auction['task'])
            del self.auctions[tid]
            self._status(f'Task {tid} queued — no eligible robots.')
            return

        self._evaluate_and_assign(tid, eligible)

    # ----------------------------------------------------------
    # EVALUATION  (weighted cost function)
    # ----------------------------------------------------------
    def _evaluate_and_assign(self, tid: str, eligible: list):
        max_eta  = max(b.eta      for b in eligible) or 1.0
        max_dist = max(b.distance for b in eligible) or 1.0
        max_nrg  = max(b.energy_level for b in eligible) or 1.0

        scored = []
        for bid in eligible:
            score = (
                self.W_ETA      * (bid.eta      / max_eta)
              + self.W_DISTANCE * (bid.distance  / max_dist)
              - self.W_ENERGY   * (bid.energy_level / max_nrg)
            )
            scored.append((score, bid))
            self.get_logger().info(
                f'  Score[{bid.robot_id}] = {score:.4f}'
            )

        scored.sort(key=lambda x: x[0])
        best_score, winner = scored[0]

        self.get_logger().info(
            f'\n[WINNER] {winner.robot_id} wins task {tid}\n'
            f'  Score={best_score:.4f} | ETA={winner.eta:.1f}s'
        )

        # Publish assignment
        msg = Assignment()
        msg.task_id          = tid
        msg.winner_robot_id  = winner.robot_id
        msg.robot_type       = winner.robot_type
        msg.eta              = winner.eta
        msg.winning_bid_cost = winner.cost
        msg.losing_robot_ids = [b.robot_id for _, b in scored[1:]]

        self.assignment_pub.publish(msg)
        self.assigned[tid] = winner.robot_id
        del self.auctions[tid]
        self._status(f'Task {tid} → {winner.robot_id}')

    # ----------------------------------------------------------
    def _status(self, msg: str):
        s = String()
        s.data = f'[TaskManager] {msg}'
        self.status_pub.publish(s)


def main(args=None):
    rclpy.init(args=args)
    node = TaskManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
