import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Create the launch description
    ld = LaunchDescription()

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
            name='robot_name',
            default_value='',
            description='Namespace de niveau supérieur'
        )
    )

    spawn_x_val = LaunchConfiguration('spawn_x_val')
    spawn_y_val = LaunchConfiguration('spawn_y_val')
    spawn_z_val = LaunchConfiguration('spawn_z_val')
    spawn_yaw_val = LaunchConfiguration('spawn_yaw_val')
    robot_name = LaunchConfiguration('robot_name')
    urdf_model = LaunchConfiguration('urdf_model')
    use_sim_time = LaunchConfiguration('use_sim_time')


    # Constants for paths to different files and folders
    package_name = 'limo_simulation'
    robot_name_in_model = robot_name
    urdf_file_path = 'urdf/limo_four_diff.xacro'
    pkg_share = FindPackageShare(package=package_name)
    default_urdf_model_path = os.path.join(pkg_share.find(package_name), urdf_file_path)


    ld.add_action(
        DeclareLaunchArgument(
            name='urdf_model',
            default_value=default_urdf_model_path,
            description='Chemin absolu vers le fichier URDF du robot'
        )
    )

    robot_description = Command([
        'xacro ', urdf_model,
        ' robot_namespace:=', robot_name,
    ])


    # Subscribe to the joint states of the robot, and publish the 3D pose of each link
    start_robot_state_publisher_cmd = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        namespace= robot_name,
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': use_sim_time}
        ],

    )

    # Launch the robot
    spawn_entity_cmd = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        namespace= robot_name,
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
    ld.add_action(spawn_entity_cmd)

    return ld

