import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Create the launch description
    ld = LaunchDescription()
    
# Declare launch arguments
    ld.add_action(
        DeclareLaunchArgument(
            name='environnement_path',
            default_value='worlds/labyrinthe1.world',
            description='path to the environment Gazebo File'
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name='env_pkg',
            default_value='limo_simulation',
            description='package of the environment'
        )
    )

    env_pkg = LaunchConfiguration('env_pkg')
    

    # Constants for paths to different files and folders
    package_name = 'limo_simulation'
    gazebo_models_path = 'models'

    # Set the path to different files and folders
    pkg_gazebo_ros = FindPackageShare(package='gazebo_ros')
    pkg_share = FindPackageShare(package=package_name)
    pkg_env_share = FindPackageShare(package=env_pkg)
    world_path = PathJoinSubstitution(     [pkg_env_share, LaunchConfiguration('environnement_path')] )
    
    gazebo_models_path_full = os.path.join(pkg_share.find(package_name), gazebo_models_path)
    os.environ["GAZEBO_MODEL_PATH"] = gazebo_models_path_full

    

    ld.add_action(
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='True',
            description='Utiliser l\'horloge de simulation (Gazebo) si vrai'
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name='headless',
            default_value='False',
            description='Exécuter sans interface graphique si vrai'
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name='namespace',
            default_value='',
            description='Namespace de niveau supérieur'
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name='use_namespace',
            default_value='False',
            description='Appliquer un namespace à la pile de navigation si vrai'
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name='use_simulator',
            default_value='True',
            description='Démarrer le simulateur si vrai'
        )
    )

    # Launch configuration variables specific to simulation
    use_sim_time = LaunchConfiguration('use_sim_time')
    headless = LaunchConfiguration('headless')
    namespace = LaunchConfiguration('namespace')
    use_namespace = LaunchConfiguration('use_namespace')
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
    use_simulator = LaunchConfiguration('use_simulator')


    # Start Gazebo server
    start_gazebo_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros.find('gazebo_ros'), 'launch', 'gzserver.launch.py')
        ),
        condition=IfCondition(use_simulator),
        launch_arguments={'world': world_path}.items()
    )

    # Start Gazebo client
    start_gazebo_client_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros.find('gazebo_ros'), 'launch', 'gzclient.launch.py')
        ),
        condition=IfCondition(PythonExpression([use_simulator, ' and not ', headless]))
    )



    # Add all actions to the launch description
    ld.add_action(start_gazebo_server_cmd)
    ld.add_action(start_gazebo_client_cmd)

    return ld

