import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import tkinter as tk
from tkinter import font

class ScoreboardNode(Node):
    def __init__(self):
        super().__init__('scoreboard_node')

        # Abonnements
        self.score1_sub = self.create_subscription(Int32, 'referee/score1', self.score1_callback, 10)
        self.score2_sub = self.create_subscription(Int32, 'referee/score2', self.score2_callback, 10)

        # Publication
        self.reset_pub = self.create_publisher(Int32, 'referee/reset_score', 10)

        # Variables pour stocker les scores
        self.score1 = 17
        self.score2 = 23

        # Initialisation de l'interface graphique
        self.root = tk.Tk()
        self.root.title("Tableau de Score")

        # Police pour le texte
        self.custom_font = font.Font(size=24)

        # Labels pour afficher les scores
        self.score1_label = tk.Label(self.root, text=f"Score 1: {self.score1}", font=self.custom_font)
        self.score1_label.pack(pady=10)

        self.score2_label = tk.Label(self.root, text=f"Score 2: {self.score2}", font=self.custom_font)
        self.score2_label.pack(pady=10)

        # Bouton pour réinitialiser les scores
        self.reset_button = tk.Button(self.root, text="Init match", command=self.reset_scores)
        self.reset_button.pack(pady=20)

        # Lancer la boucle de mise à jour ROS 2
        self.root.after(100, self.update_gui)

    def update_gui(self):
        rclpy.spin_once(self, timeout_sec=0.1)
        self.root.after(100, self.update_gui)  # Rappelle update_gui toutes les 100ms


    def score1_callback(self, msg):
        self.score1 = msg.data
        self.score1_label.config(text=f"Score 1: {self.score1}")
        #self.get_logger().info('score 1 modif : %d ' %(self.score1))

    def score2_callback(self, msg):
        self.score2 = msg.data
        self.score2_label.config(text=f"Score 2: {self.score2}")
        self.get_logger().info('score 2 modif : %d ' %(self.score2))

    def reset_scores(self):
        self.reset_pub.publish(Int32(data=1))
        self.score1_label.config(text=f"Score 1: {self.score1}")
        self.score2_label.config(text=f"Score 2: {self.score2}")

def main(args=None):
    rclpy.init(args=args)
    node = ScoreboardNode()
    node.root.mainloop()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
