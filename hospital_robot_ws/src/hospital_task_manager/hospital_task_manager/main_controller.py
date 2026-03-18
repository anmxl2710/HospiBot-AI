import rclpy
from rclpy.node import Node

from hospital_task_manager.tasks.task_queue import TaskQueue
from hospital_task_manager.tasks.scheduler import Scheduler
from hospital_task_manager.robots.robot_manager import RobotManager
from hospital_task_manager.robots.robot import Robot
from hospital_task_manager.auction.auction_allocator import AuctionAllocator
from hospital_task_manager.nlp.task_parser import parse_task
from hospital_task_manager.ros.ros_interface import ROSInterface
from hospital_task_manager.dashboard.dashboard import get_user_task


class TaskController(Node):

    def __init__(self):

        super().__init__("task_controller")

        # Robots in the system
        self.robots = [

            Robot("cleaner_robot_1","clean",90,(4,9)),
            Robot("cleaner_robot_2","clean",80,(1,3)),
            Robot("sample_robot_1","sample",70,(2,2)),
            Robot("sample_robot_2","sample",60,(5,4)),
            Robot("hybrid_robot","hybrid",95,(0,0))

        ]

        self.auction = AuctionAllocator()
        self.task_queue = TaskQueue()
        self.robot_manager = RobotManager(self.robots)
        self.scheduler = Scheduler(self.robot_manager, self.auction)
    def run(self):

      while True:

        text = get_user_task()

        task = parse_task(text)

        print("Task created:", task)

        self.task_queue.add_task(task)

        if self.task_queue.has_tasks():

            next_task = self.task_queue.get_next_task()

            winner = self.scheduler.schedule(next_task)

            if winner:

                print("Winner robot:", winner.name)

                ros = ROSInterface(self, winner.name)

                ros.move_forward()

            else:

                print("No robots available, task waiting in queue")


def main(args=None):

    rclpy.init(args=args)

    node = TaskController()

    node.run()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
