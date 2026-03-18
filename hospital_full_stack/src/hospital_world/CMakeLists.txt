cmake_minimum_required(VERSION 3.8)
project(hospital_world)

find_package(ament_cmake REQUIRED)

# Install world files and robot models so ROS2 can find them
install(DIRECTORY
  worlds
  robots
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
