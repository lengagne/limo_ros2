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
            name='spawn_x_val',
            default_value='0.0',
            description='x position of the robot'
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name='spawn_y_val',
            default_value='1.0',
            description='y position of the robot'
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name='spawn_z_val',
            default_value='0.0',
            description='z position of the robot'
        )
    )


    ld.add_action(
        DeclareLaunchArgument(
            name='spawn_yaw_val',
            default_value='1.57',
            description='z orientation of the robot'
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name='env_pkg',
            default_value='limo_simulation',
            description='package of the environment'
        )
    )
    

    # Constants for paths to different files and folders
    package_name = 'limo_simulation'
    gazebo_models_path = 'models'
    robot_name_in_model = 'limo_simulation'
    urdf_file_path = 'urdf/limo_four_diff.xacro'

    # Pose where we want to spawn the robot
    spawn_x_val = LaunchConfiguration('spawn_x_val')   
    spawn_y_val = LaunchConfiguration('spawn_y_val')   
    spawn_z_val = LaunchConfiguration('spawn_z_val')   
    spawn_yaw_val = LaunchConfiguration('spawn_yaw_val')   
    env_pkg = LaunchConfiguration('env_pkg')

    # Set the path to different files and folders
    pkg_gazebo_ros = FindPackageShare(package='gazebo_ros')
    pkg_share = FindPackageShare(package=package_name)
    pkg_env_share = FindPackageShare(package=env_pkg)
    default_urdf_model_path = os.path.join(pkg_share.find(package_name), urdf_file_path)
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
            name='urdf_model',
            default_value=default_urdf_model_path,
            description='Chemin absolu vers le fichier URDF du robot'
        )
    )

    ld.add_action(
        DeclareLaunchArgument(
            name='use_robot_state_pub',
            default_value='True',
            description='Démarrer le publisher d\'état du robot si vrai'
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
    urdf_model = LaunchConfiguration('urdf_model')
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
    use_simulator = LaunchConfiguration('use_simulator')

    # Subscribe to the joint states of the robot, and publish the 3D pose of each link
    start_robot_state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': Command(['xacro ', urdf_model])},
            {'use_sim_time': use_sim_time}
        ]
    )

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

    # Launch the robot
    spawn_entity_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', robot_name_in_model,
            '-topic', 'robot_description',
            '-x', spawn_x_val,
            '-y', spawn_y_val,
            '-z', spawn_z_val,
            '-Y', spawn_yaw_val
        ],
        output='screen'
    )

    # Add all actions to the launch description
    ld.add_action(start_robot_state_publisher_cmd)
    ld.add_action(start_gazebo_server_cmd)
    ld.add_action(start_gazebo_client_cmd)
    ld.add_action(spawn_entity_cmd)

    return ld

