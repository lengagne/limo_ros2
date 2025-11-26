import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():
    # Nom du package
    package_name = 'limo_arena'
    package_env_name = 'limo_simulation'

    # Crée la description de launch
    ld = LaunchDescription()

    # Chemin vers le fichier gazebo_simulation_common.launch.py
    simulation_launch_path = os.path.join(
        get_package_share_directory(package_env_name),
        'launch',
        'gazebo_simulation_common.launch.py'
    )

    # Chemin vers le fichier gazebo_simulation_common.launch.py
    spawn_robot_launch_path = os.path.join(
        get_package_share_directory(package_env_name),
        'launch',
        'gazebo_spawn_common.launch.py'
    )


    simulation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(simulation_launch_path),
        launch_arguments={
            'environnement_path': 'worlds/arena.world',  # Chemin relatif
            'env_pkg': package_name,
        }.items()
    )

    # Inclut le fichier gazebo_simulation_common.launch.py et modifie ses paramètres
    spawn_robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(spawn_robot_launch_path),
        launch_arguments={
            'spawn_x_val': '1.5',
            'spawn_y_val': '0.0',
            'spawn_z_val': '0.0',
            'spawn_yaw_val': '3.14',
        }.items()
    )

    ## Add referee
    referee_node = Node(
        package=package_name,  # Remplace par le nom du package contenant le nœud referee
        executable='referee',  # Remplace par le nom de l'exécutable du nœud referee
        name='referee',
        output='screen',  # Affiche la sortie du nœud dans le terminal
    )

    ld.add_action(simulation_launch)
    ld.add_action(spawn_robot_launch)
    ld.add_action(referee_node)

    return ld
