#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this python file is used to record the laser data and the position of the robot


import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan as Laser
from geometry_msgs.msg import PoseStamped

from nav_msgs.msg import Odometry
import json
import math
import time

distance = 0
command = 1 #1: go to the end point, 0: stop, 2: go to the start point
file_number = 1

# 坐标位置
start_point = {"name": "start", "positionx": 0.0, "positiony": 0.0, "orientationz": 0.0,"orientationw": 1.0}
end_point = {"name": "end", "positionx": 8.089402198791504, "positiony": 8.514765739440918, "orientationz": -0.6975137356110925,"orientationw": 0.7165714120964211}

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

    # def goal_callback(self, msg):
    #     self.goalx = msg.pose.position.x
    #     self.goaly = msg.pose.position.y
    #     self.goalz = msg.pose.orientation.z
    #     self.goalw = msg.pose.orientation.w
    #     self.goal = msg

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
        
    def send_navigation_goal(self, location) -> None:
        """
        Sends a navigation goal to the action server.

        :param location: A dictionary containing the location information (name, x, y, theta).
        """
        goal_msg = PoseStamped()
        goal_msg.header.stamp = self.get_clock().now().to_msg()
        goal_msg.header.frame_id = 'map'
        goal_msg.pose.position.x = location["positionx"]
        goal_msg.pose.position.y = location["positiony"]
        goal_msg.pose.position.z = 0.0
        goal_msg.pose.orientation.x = 0.0
        goal_msg.pose.orientation.y = 0.0
        goal_msg.pose.orientation.z = location["orientationz"]
        goal_msg.pose.orientation.w = location["orientationw"]
        self.goal_pose_publisher.publish(goal_msg)
    

    def listener_callback(self, data):
        global command 
        global file_number
        # 从初始位置运行到终点记录沿途的数据，distance小于0.3时停止并返回起点。
        if command == 1:
            location = end_point
            self.send_navigation_goal(location)

            distance = self.get_distance(self.speed, end_point)
            # print(self.posz)
            if distance is not None:
                #将数据保存为json格式
                ranges = data.ranges
                # print(ranges)
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
                with open(f'data2/laser_data{file_number}.json', 'a') as f:
                    json.dump(data, f)
                    f.write('\n')
                if distance < 0.3:
                    command = 2
                    print("back to start point")
        # 从终点返回到起点
        if command == 2:
            location = start_point
            self.send_navigation_goal(location)
            distance = self.get_distance(self.speed, start_point)
            print("self.posz:",self.posz,"distance:",distance)
            if distance is not None and distance < 0.3 and self.posz>-0.2:
                time.sleep(0.5)
                command = 1
                file_number += 1
                print("back to end point")





def main(args=None):
    rclpy.init(args=args)
    node = LaserSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
