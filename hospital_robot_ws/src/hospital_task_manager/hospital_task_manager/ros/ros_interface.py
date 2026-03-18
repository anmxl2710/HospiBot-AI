import rclpy
from geometry_msgs.msg import Twist

class ROSInterface:

    def __init__(self, node, robot_name):

        topic = f"/{robot_name}/cmd_vel"

        self.publisher = node.create_publisher(
            Twist,
            topic,
            10
        )

    def move_forward(self):

        msg = Twist()
        msg.linear.x = 0.5

        self.publisher.publish(msg)

    def stop(self):

        msg = Twist()
        self.publisher.publish(msg)
