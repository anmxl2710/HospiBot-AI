cmake_minimum_required(VERSION 3.8)
project(hospital_robot_sim)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(hospital_robot_sim_msgs REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  scripts/task_manager_node.py
  scripts/auction_node.py
  scripts/robot_controller_node.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  worlds
  urdf
  launch
  config
  rviz
  models
  DESTINATION share/${PROJECT_NAME}
)

ament_package()

