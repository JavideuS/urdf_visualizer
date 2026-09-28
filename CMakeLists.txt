cmake_minimum_required(VERSION 3.8)
project(urdf_visualizer)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(urdf REQUIRED)
find_package(xacro REQUIRED)

# Install launch files
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# Install RViz config
install(DIRECTORY rviz
  DESTINATION share/${PROJECT_NAME}
)

# Install Scripts
install(PROGRAMS 
  scripts/auto_reload_urdf.py
  scripts/simulate.py
  DESTINATION share/${PROJECT_NAME}/scripts
)

ament_package()
