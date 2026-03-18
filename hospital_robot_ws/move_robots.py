import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class HospitalRobotController(Node):

    def __init__(self):
        super().__init__('hospital_robot_controller')

        self.cleaner1 = self.create_publisher(Twist, '/cleaner_robot_1/cmd_vel', 10)
        self.cleaner2 = self.create_publisher(Twist, '/cleaner_robot_2/cmd_vel', 10)
        self.sample1 = self.create_publisher(Twist, '/sample_robot_1/cmd_vel', 10)
        self.sample2 = self.create_publisher(Twist, '/sample_robot_2/cmd_vel', 10)
        self.hybrid = self.create_publisher(Twist, '/hybrid_robot/cmd_vel', 10)

        self.timer = self.create_timer(0.5, self.move_robots)

    def move_robots(self):

        msg = Twist()

        # Cleaner robots move forward slowly
        msg.linear.x = 0.5
        msg.angular.z = 0.0
        self.cleaner1.publish(msg)
        self.cleaner2.publish(msg)

        # Sample robots rotate slowly
        msg.linear.x = 0.2
        msg.angular.z = 0.3
        self.sample1.publish(msg)
        self.sample2.publish(msg)

        # Hybrid robot patrol
        msg.linear.x = 0.4
        msg.angular.z = -0.2
        self.hybrid.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = HospitalRobotController()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
