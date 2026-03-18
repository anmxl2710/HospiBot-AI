cmake_minimum_required(VERSION 3.8)
project(hospital_world)

find_package(ament_cmake REQUIRED)

# Install launch files
install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# Install world files
install(
  DIRECTORY worlds
  DESTINATION share/${PROJECT_NAME}
)

# Install robot models
install(
  DIRECTORY models
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
