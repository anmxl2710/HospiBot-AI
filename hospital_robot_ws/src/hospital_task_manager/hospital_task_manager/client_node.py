#!/usr/bin/env python3
"""
Hospital Client Node
====================
Generates tasks matching the actual hospital.world layout.

Room coordinates extracted from hospital.world:
  bed_1 → (-8.257, -5.543)   patient_room_1
  bed_2 → (-8.254, -0.776)   patient_room_2
  bed_3 → (-8.251,  4.001)   patient_room_3
  bed_4 → (-8.243,  8.709)   patient_room_4
  cleaner_robot_1 → (4.219,  9.199)   → near top-right (pharmacy/ICU area)
  cleaner_robot_2 → (-4.123, 9.139)   → near top-center
  hybrid_robot    → (-6.743, 6.098)   → upper-left corridor
"""

import rclpy
from rclpy.node import Node
import uuid

from fleet_interfaces.msg import Task
from std_msgs.msg import String


# Exact coordinates from your hospital.world
ROOMS = {
    'patient_room_1':  (-8.257, -5.543),
    'patient_room_2':  (-8.254, -0.776),
    'patient_room_3':  (-8.251,  4.001),
    'patient_room_4':  (-8.243,  8.709),
    'lab':             ( 4.219,  9.199),   # top-right section
    'pharmacy':        (-4.123,  9.139),   # top-center section
    'icu':             (-6.743,  6.098),   # upper-left
    'corridor_center': ( 0.000,  0.000),
    'charging_dock':   ( 0.000, -9.000),
}

DEMO_TASKS = [
    dict(task_type='deliver_sample',
         pickup='patient_room_1', dropoff='lab', priority=3),

    dict(task_type='clean',
         pickup='corridor_center', dropoff='corridor_center', priority=1),

    dict(task_type='deliver_medicine',
         pickup='pharmacy', dropoff='patient_room_4', priority=4),

    dict(task_type='deliver_sample',
         pickup='patient_room_3', dropoff='lab', priority=2),

    dict(task_type='clean',
         pickup='icu', dropoff='icu', priority=2),

    dict(task_type='deliver_sample',
         pickup='patient_room_2', dropoff='lab', priority=3),
]


class ClientNode(Node):

    def __init__(self):
        super().__init__('hospital_client')
        self.pub = self.create_publisher(Task, '/hospital/new_task', 10)
        self._idx = 0

        self.get_logger().info('Hospital Client ready.')
        self.get_logger().info(
            'Sending first task in 5s, then one every 8s...')

        # First task after 5s, then every 8s
        self.create_timer(5.0, self._send_next)

    def _send_next(self):
        if self._idx >= len(DEMO_TASKS):
            self.get_logger().info('All demo tasks sent!')
            return

        d = DEMO_TASKS[self._idx]
        self._idx += 1

        task = Task()
        task.task_id          = f'T{self._idx:03d}_{str(uuid.uuid4())[:4]}'
        task.task_type        = d['task_type']
        task.pickup_location  = d['pickup']
        task.dropoff_location = d['dropoff']
        task.priority         = d['priority']
        task.status           = 'pending'

        px, py = ROOMS[d['pickup']]
        dx, dy = ROOMS[d['dropoff']]
        task.pickup_x  = px;  task.pickup_y  = py
        task.dropoff_x = dx;  task.dropoff_y = dy

        pri = {1:'LOW', 2:'MEDIUM', 3:'HIGH', 4:'EMERGENCY'}.get(
            d['priority'], '?')
        self.get_logger().info(
            f'\n[CLIENT] Sending task {task.task_id}\n'
            f'  Type   : {task.task_type}\n'
            f'  Route  : {d["pickup"]} → {d["dropoff"]}\n'
            f'  Priority: {pri}'
        )
        self.pub.publish(task)

        # Schedule next task in 8s (gives auction time to finish)
        self.create_timer(8.0, self._send_next)


def main(args=None):
    rclpy.init(args=args)
    node = ClientNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
