import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from std_msgs.msg import Int32
from gazebo_msgs.msg import ModelStates
from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState
from gazebo_msgs.srv import SpawnEntity


class BallonSpawner(Node):
    def __init__(self):
        super().__init__('ballon_spawner')
        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service /spawn_entity not available, waiting...')

        self.ballon_names = [f"ballon_{i}" for i in range(5)]
        for i in range(5):
            self.spawn_ballon(self.ballon_names[i],-1.0 + 0.5*i)
        
        
        self.subscription = self.create_subscription(
            ModelStates,
            '/gazebo/model_states',
            self.model_states_callback,
            10)
        
        self.subscription_reset = self.create_subscription( Int32, '/reset_score', self.reset_score,10)
        
        self.client = self.create_client(SetEntityState, '/gazebo/set_entity_state')
        self.ballon_name = "ballon"
        self.goal_line = 1.5  # Coordonnée x de la ligne de but
        
        
        self.score1 = 0
        self.score2 = 0
        
    def model_states_callback(self, msg):
        try:
            for i in range(5):
                index = msg.name.index(self.ballon_names[i])
                x = msg.pose[index].position.x
                if x > self.goal_line:
                    self.score1 += 1
                    self.reset_ballon(self.ballon_names[i])
                    
                if x < - self.goal_line:
                    self.score2 += 1
                    self.reset_ballon(self.ballon_names[i])                    
                    
        except ValueError:
            pass        
        
    def reset_ballon(self,name):
        self.get_logger().info('Reset ball {name}')
        self.get_logger().info('Score : %d : %d' %(self.score1, self.score2))
        request = SetEntityState.Request()
        request.state.name = name
        request.state.pose.position.x = 0.0
        request.state.pose.position.y = 0.0
        request.state.pose.position.z = 0.5
        self.client.call_async(request)

    def reset_score(self,msg):
        self.get_logger().info('Reset Score')
        self.score1 = 0
        self.score2 = 0
        self.get_logger().info('Score : %d : %d' %(self.score1, self.score2))

    def spawn_ballon(self, name,y):
        request = SpawnEntity.Request()
        request.name = name
        request.xml = """
        <?xml version="1.0"?>
        <sdf version="1.6">
          <model name="ballon">
            <pose>0 0 0.5 0 0 0</pose>
            <link name="link">
                <inertial>
                    <mass>0.45</mass> 
                    <inertia>
                    <ixx>0.0018</ixx> 
                    <iyy>0.0018</iyy>
                    <izz>0.0018</izz>
                    </inertia>
                </inertial>            
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
        request.initial_pose.position.z = 0.2
        request.reference_frame = "world"

        future = self.spawn_client.call_async(request)
        future.add_done_callback(self.spawn_callback)

    def spawn_callback(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info('Ballon spawned successfully!')
            else:
                self.get_logger().error('Failed to spawn ballon: ' + response.status_message)
        except Exception as e:
            self.get_logger().error('Service call failed: %r' % (e,))

def main(args=None):
    rclpy.init(args=args)
    node = BallonSpawner()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

