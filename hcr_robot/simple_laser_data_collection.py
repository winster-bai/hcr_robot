#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 用于简单障碍物的激光雷达数据采集，手动控制机器人运动到终点，记录沿途的激光雷达数据


import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan as Laser
from geometry_msgs.msg import PoseStamped

from nav_msgs.msg import Odometry
import json
import math
import time

distance = 0
run = 0

# 坐标位置
start_point = {"name": "start", "positionx": 0.0, "positiony": 0.0, "orientationz": 0.0,"orientationw": 1.0}
end_point = {"name": "end", "positionx": 6.0, "positiony": 0.0, "orientationz": 0.0,"orientationw": 1.0}

class LaserSubscriber(Node):
    def __init__(self):
        super().__init__('speed_subscriber')
        self.sub = self.create_subscription(Laser, '/scan', self.listener_callback, 10)
        self.speed_subscriber = self.create_subscription(Odometry, "/odom", self.pose_callback, 10) # 当前位置和速度节点
        # self.goal_subscription = self.create_subscription(PoseStamped, '/goal_pose',self.goal_callback, 10) # 目的地位置信息节点
        self.goal_pose_publisher = self.create_publisher(PoseStamped, '/goal_pose', 10) # 发布目的地位置到节点
        
        self.posx = 0.0  # 当前位置x
        self.posx = 0.0  # 当前位置x
        self.posy  = 0.0  # 当前位置y
        self.posz  = 0.0  # 当前位置朝向z
        self.posw  = 0.0  # 当前位置朝向w
        self.speedx = 0.0  # 线速度x
        self.speedy  = 0.0  # 线速度y
        self.speedz  = 0.0  # 角速度z
        self.speed = Odometry()

        self.goalx = 0.0  # 目标位置坐标
        self.goaly = 0.0
        self.goalz = 0.0
        self.goalw = 0.0
        self.goal = PoseStamped()


    def pose_callback(self, msg): # 获取当前位置和速度
        self.posx = msg.pose.pose.position.x
        self.posy = msg.pose.pose.position.y
        self.posz = msg.pose.pose.orientation.z
        self.posw = msg.pose.pose.orientation.w
        self.speedx = msg.twist.twist.linear.x
        self.speedy = msg.twist.twist.linear.y
        self.speedz = msg.twist.twist.angular.z
        self.speed = msg
        
        # print (self.z) #used for debegging


    def get_distance(self, start, location):
        goal_msg = PoseStamped()
        goal_msg.header.stamp = self.get_clock().now().to_msg()
        goal_msg.header.frame_id = 'map'
        goal_msg.pose.position.x = location["positionx"]
        goal_msg.pose.position.y = location["positiony"]
        # print("goal_pos:",goal_msg.pose.position.x,goal_msg.pose.position.y)
        return math.sqrt(((goal_msg.pose.position.x-start.pose.pose.position.x)**2 + (goal_msg.pose.position.y-start.pose.pose.position.y)**2))

        # if goal_msg.pose.position.x !=0.0 and goal_msg.pose.position.y !=0.0 :
        #     return math.sqrt(((goal_msg.pose.position.x-start.pose.pose.position.x)**2 + (goal_msg.pose.position.y-start.pose.pose.position.y)**2))
        # else:
        #     # print("plz set the distanation")
        #     return None
        
    

    def listener_callback(self, data):
        location = end_point
        distance = self.get_distance(self.speed, end_point)
        print("self.posz:",self.posz,"distance:",distance)
        if distance is not None:
            #将数据保存为json格式
            ranges = data.ranges
            #将数据保存为json格式
            data = {"laser": list(ranges)}  # 将ranges转换为列表
            speed = [self.speedx, self.speedy, self.speedz]
            position = [self.posx, self.posy, self.posz, self.posw]
            goal = [location["positionx"], location["positiony"], location["orientationz"], location["orientationw"]]
            data["speed"] = speed
            data["position"] = position
            data["goal"] = goal
            data["distance"] = distance
            # print("content2:", data)
            # if self.speedx > 0.03:
            #     self.run = 1
            # if self.run == 1:
            with open(f'obstacle_data/obstacle_data_hand.json', 'a') as f:
                json.dump(data, f)
                f.write('\n')


def main(args=None):
    rclpy.init(args=args)
    node = LaserSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
