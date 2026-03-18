cmake_minimum_required(VERSION 3.8)
project(hospital_robot_sim_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Task.msg"
  "msg/TaskAssignment.msg"
  "msg/AuctionResult.msg"
  "msg/RobotStatus.msg"
  DEPENDENCIES builtin_interfaces
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()

