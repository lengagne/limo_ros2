The project was initially forked from : https://github.com/agilexrobotics/limo_ros2/tree/foxy

This project is set for academic purpose. The goal is to provide a light environment for the simulation of the Limo robot under ROS-2.

This project is used in a VirtualBox with Ubuntu-Mate 2022 and ROS2-foxy.


# Install essential packages
apt-get update \
    && apt-get install -y --no-install-recommends \	
    libusb-1.0-0 \
    udev \
    apt-transport-https \
    ca-certificates \
    curl \
    swig \
    software-properties-common \
    python3-pip


## Create workspace
```
mkdir ~/agilex_ros2_ws
cd ~/agilex_ros2_ws
mkdir src
cd src
git clone git@github.com:lengagne/limo_ros2.git -b foxy
```

# Run Gazebo Simulation
```
ros2 launch limo_simulation gazebo_simulation.launch.py 
```

# Compile limo_ros2 packages
```
cd ~/```
colcon build
source install/setup.bash
```



# Install Docker and necessary files on the Limo

To do
```






