import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_share_dir = get_package_share_directory('urdf_visualizer')
    script_path = os.path.join(pkg_share_dir, 'scripts', 'simulate.py')

    return LaunchDescription([
        DeclareLaunchArgument(name='model', 
                              description='Absolute path to robot urdf file'),

        ExecuteProcess(
            cmd=[script_path, LaunchConfiguration('model')],
            output='screen'
        )
    ])
