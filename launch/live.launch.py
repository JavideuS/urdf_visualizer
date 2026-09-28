import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share_dir = get_package_share_directory('urdf_visualizer')
    default_rviz_config_path = os.path.join(pkg_share_dir, 'rviz', 'view.rviz')
    # The script is installed to share/urdf_visualizer/scripts/
    reload_script_path = os.path.join(pkg_share_dir, 'scripts', 'auto_reload_urdf.py')

    return LaunchDescription([
        DeclareLaunchArgument(name='model', 
                              description='Absolute path to robot urdf file'),
        DeclareLaunchArgument(name='rvizconfig', default_value=default_rviz_config_path,
                                            description='Absolute path to rviz config file'),

        # Launch RViz2 separately as a standard node
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', LaunchConfiguration('rvizconfig')],
        ),

        # Execute the auto-reload script in --no-rviz mode
        # This script handles running/restarting robot_state_publisher and joint_state_publisher automatically
        ExecuteProcess(
            cmd=[reload_script_path, LaunchConfiguration('model'), '--no-rviz'],
            output='screen'
        )
    ])
