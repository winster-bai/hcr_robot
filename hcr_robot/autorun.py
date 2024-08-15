#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this python file is used to auto run the robot with h5 model

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan as Laser

from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist 
import math
import os

import tensorflow as tf
import numpy as np

# tf.config.experimental.set_visible_devices([], 'GPU')

# 坐标位置
start_point = {"name": "start", "positionx": 0.0, "positiony": 0.0, "orientationz": 0.0,"orientationw": 1.0}
end_point = {"name": "end", "positionx": 6.0, "positiony": 0.0, "orientationz": 0.0,"orientationw": 1.0}

model_path = os.path.abspath('model/model_combined_AB.h5')
model = tf.keras.models.load_model(model_path)

class SpeedPub(Node):
    def __init__(self):
        super().__init__('speed_publisher')
        self.sub = self.create_subscription(Laser, '/scan', self.listener_callback, 10) # 订阅激光雷达数据
        self.speed_subscriber = self.create_subscription(Odometry, "/odom", self.pose_callback, 10) # 当前位置和速度节点
        self.speed_publisher = self.create_publisher(Twist, "/cmd_vel", 10) # 发布速度到节点
        
        self.posx = 0.0  # 当前位置x
        self.posy  = 0.0  # 当前位置y
        self.posz  = 0.0  # 当前位置朝向z
        self.posw  = 0.0  # 当前位置朝向w
        self.speedx = 0.0  # 线速度x
        self.speedy  = 0.0  # 线速度y
        self.speedz  = 0.0  # 角速度z
        self.speed = Odometry()

    def pose_callback(self, msg): # 获取当前位置和速度
        self.posx = msg.pose.pose.position.x
        self.posy = msg.pose.pose.position.y
        self.posz = msg.pose.pose.orientation.z
        self.posw = msg.pose.pose.orientation.w
        self.speedx = msg.twist.twist.linear.x
        self.speedy = msg.twist.twist.linear.y
        self.speedz = msg.twist.twist.angular.z
        self.speed = msg

    


    def get_distance(self, start, location):
        endpointx = location["positionx"]
        endpointy = location["positiony"]
        return math.sqrt(((endpointx-start.pose.pose.position.x)**2 + (endpointy-start.pose.pose.position.y)**2))

    
    def calculate_angle(self, position, goal):
        delta_y = goal[1] - position[1]
        delta_x = goal[0] - position[0]
        angle = np.arctan2(delta_y, delta_x)
        return angle

    def listener_callback(self, data):

        location = end_point        
        distance = self.get_distance(self.speed, location)
        if distance is not None:
            #读取激光雷达数据
            ranges = data.ranges
            #将数据保存为json格式
            ranges = list(ranges) # 将ranges转换为列表
            # print("ranges: ", ranges)
            laser_data = np.array([-1 if x == float('Infinity') else x for x in ranges])
            # speed = [self.speedx, self.speedy, self.speedz] # speed在预测时没有用到
            position = [self.posx, self.posy, self.posz, self.posw]
            goal = [location["positionx"], location["positiony"], location["orientationz"], location["orientationw"]]
            angle = self.calculate_angle(position, goal)
            # print("laser_data: ", laser_data, "laser_data shape: ", laser_data.shape)
            # print("position: ", position)
            # print("distance: ", distance)
            # print("angle: ", angle)
            input_data = np.concatenate([laser_data, position, [distance],[angle]])
            # print("inputshape",input_data.shape)
            input_data = np.array([input_data])
            predictions = model.predict(input_data)

            # print("prediction: ", predictions)
            # print(len(predictions))  #2

            # 使用 np.argmax 来找到最大值的索引
            linear_speeds = np.argmax(predictions[0]) * (0.3/100)
            angular_speeds = np.argmax(predictions[1]) * (1/100) - 0.5
            print("角速度：",angular_speeds)



            # 发送predictions到速度节点
            self.speedx = float(linear_speeds)
            # self.speedy = float(predictions[0][1])
            self.speedy = 0.0
            self.speedz = float(angular_speeds)
            print("speedx: ", self.speedx, "speedy: ", self.speedy, "speedz: ", self.speedz)
            twist_msg = Twist()
            twist_msg.linear.x = self.speedx
            twist_msg.linear.y = self.speedy
            twist_msg.angular.z = self.speedz
            self.speed_publisher.publish(twist_msg)






def main(args=None):
    rclpy.init(args=args)
    node = SpeedPub()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
