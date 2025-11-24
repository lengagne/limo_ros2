import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Nom du package
    package_name = 'limo_simulation'

    # Crée la description de launch
    ld = LaunchDescription()

    # Chemin vers le fichier gazebo_simulation_common.launch.py
    spawn_robot_launch_path = os.path.join(
        get_package_share_directory(package_name),
        'launch',
        'gazebo_simulation_common.launch.py'
    )

    # Inclut le fichier gazebo_simulation_common.launch.py et modifie ses paramètres
    spawn_robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(spawn_robot_launch_path),
        launch_arguments={
            'environnement_path': 'worlds/labyrinthe4.world',  # Chemin relatif
            'spawn_x_val': '-12.5',
            'spawn_y_val': '3.0',
            'spawn_z_val': '0.5',
            'spawn_yaw_val': '-1.57',
        }.items()
    )

    ld.add_action(spawn_robot_launch)

    return ld



