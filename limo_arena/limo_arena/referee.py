import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from std_msgs.msg import Int32
from gazebo_msgs.msg import ModelStates
from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState
from gazebo_msgs.srv import SpawnEntity
from geometry_msgs.msg import Wrench
import random


class BallonSpawner(Node):
    def __init__(self):
        super().__init__('ballon_spawner')
        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')

        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service /spawn_entity not available, waiting...')

        self.nb_ballon =5

        self.ballon_names = [f"ballon_{i}" for i in range(self.nb_ballon)]
        for i in range(self.nb_ballon):
            self.spawn_ballon(self.ballon_names[i],-1.0 + 0.5*i)
        
        self.subscription = self.create_subscription( ModelStates, '/gazebo/model_states', self.model_states_callback, 10)

        self.subscription_reset = self.create_subscription( Int32, '/reset_score', self.reset_score,10)
        
        self.client = self.create_client(SetEntityState, '/gazebo/set_entity_state')
        self.goal_line = 1.5  # Coordonnée x de la ligne de but
        
        
        self.score1 = 0
        self.score2 = 0
        
    def model_states_callback(self, msg):
        try:
            for i in range(self.nb_ballon):
                index = msg.name.index(self.ballon_names[i])
                x = msg.pose[index].position.x
                y = msg.pose[index].position.y
                z = msg.pose[index].position.z
                if x > self.goal_line:
                    self.score1 += 1
                    self.reset_ballon(self.ballon_names[i])
                    return
                    
                if x < - self.goal_line:
                    self.score2 += 1
                    self.reset_ballon(self.ballon_names[i])
                    return

                if y < - 1.25:
                  request = SetEntityState.Request()
                  request.state.name = self.ballon_names[i]
                  request.state.pose.position.x = x
                  request.state.pose.position.y = y +0.01
                  request.state.pose.position.z = z
                  self.client.call_async(request)

                if y > 1.25:
                  request = SetEntityState.Request()
                  request.state.name = self.ballon_names[i]
                  request.state.pose.position.x = x
                  request.state.pose.position.y = y -0.01
                  request.state.pose.position.z = z
                  self.client.call_async(request)

        except ValueError:
            pass

    def handle_response(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"Force appliquée avec succès : {response.success}")
        except Exception as e:
            self.get_logger().error(f"Erreur : {e}")
        
    def reset_ballon(self,name):
        self.get_logger().info('Reset ball {name}')
        self.get_logger().info('Score : %d : %d' %(self.score1, self.score2))
        request = SetEntityState.Request()
        request.state.name = name
        request.state.pose.position.x = 0.0
        request.state.pose.position.y = 0.0 + random.uniform(-0.5, 0.5)
        request.state.pose.position.z = 0.5 + random.uniform(-0.5, 0.5)
        self.client.call_async(request)

    def reset_score(self,msg):
        self.get_logger().info('Reset Score')
        self.score1 = 0
        self.score2 = 0
        self.get_logger().info('Score : %d : %d' %(self.score1, self.score2))

    def spawn_ballon(self, name,y):
        request = SpawnEntity.Request()
        request.name = name
        request.xml = f"""
        <?xml version="1.0"?>
        <sdf version="1.6">
          <model name="{name}">
            <pose>0 0 0.5 0 0 0</pose>
            <link name="link">
                <inertial>
                    <mass>0.3</mass>
                      <inertia>
                      <ixx>0.0018</ixx>
                      <iyy>0.0018</iyy>
                      <izz>0.0018</izz>
                    </inertia>
                </inertial>
                <velocity_decay>
                  <linear>0.001</linear>
                  <angular>0.001</angular>
                </velocity_decay>
              <visual name="visual">
                <geometry>
                  <sphere>
                    <radius>0.11</radius>
                  </sphere>
                </geometry>
                <material>
                  <ambient>1 0 0 1</ambient>
                  <diffuse>1 0 0 1</diffuse>
                </material>
              </visual>
              <collision name="collision">
                <geometry>
                  <sphere>
                    <radius>0.11</radius>
                  </sphere>
                </geometry>
              </collision>
            </link>
          </model>
        </sdf>
        """
        request.robot_namespace = ""
        request.initial_pose = Pose()
        request.initial_pose.position.x = 0.0
        request.initial_pose.position.y = y
        request.initial_pose.position.z = 0.1
        request.reference_frame = "world"

        future = self.spawn_client.call_async(request)
        future.add_done_callback(self.spawn_callback)

    def spawn_callback(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info('Ballon spawned successfully!')
            else:
                self.get_logger().error('Failed to spawn {name}: ' + response.status_message)
        except Exception as e:
            self.get_logger().error('Service call failed: %r' % (e,))

def main(args=None):
    rclpy.init(args=args)
    node = BallonSpawner()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

