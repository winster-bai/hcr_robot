#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# this python file is used to auto run the robot with LSTM h5 model

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan as Laser
from geometry_msgs.msg import PoseStamped


from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist 
import math
import os

import tensorflow as tf
import numpy as np
from collections import deque

tf.config.experimental.set_visible_devices([], 'GPU')


class SpeedPub(Node):
    def __init__(self):
        super().__init__('speed_publisher')
        self.sub = self.create_subscription(Laser, '/scan', self.listener_callback, 10) # 订阅激光雷达数据
        self.speed_publisher = self.create_publisher(Twist, "/cmd_vel", 10) # 发布速度到节点
        
        self.speedx = 0.0  # 线速度x
        self.speedy  = 0.0  # 线速度y
        self.speedz  = 0.0  # 角速度z
        self.speed = Odometry()

        #创建一个长度为10的队列
        self.laser_data = deque(maxlen=10)

    #创建一个滑动窗口
    def create_dataset(X, y, time_steps=1):
        Xs, ys = [], []
        for i in range(len(X) - time_steps):
            v = X[i:(i + time_steps)]
            Xs.append(v)        
            ys.append(y[i + time_steps])
        return np.array(Xs), np.array(ys)

    def lstm_model(self, data):
        model_path = os.path.abspath('model/model5.h5')
        model = tf.keras.models.load_model(model_path)
        # model = tf.keras.models.load_model('./model/model.h5')

        data = np.array(data).reshape(1, 10, 360)
        predictions = model.predict(data)
        # print(predictions.shape)
        # print(predictions[0]) #predictions[0]是x_test中的t1～t10窗口预测出来的t11时刻的速度值
        # print("predictions: ", predictions)
        return predictions

    def listener_callback(self, data):
        

        #读取激光雷达数据
        ranges = data.ranges
        # print(ranges)
        #将数据保存为json格式
        self.laser_data.append(list(ranges)) # 将ranges转换为列表
        # twist = [self.speedx, self.speedy, self.speedz]
        # data["twist"] = twist

        if len(self.laser_data) == 10:
            laser_data_array = np.array(self.laser_data)
            # print("laser_data_array: ", laser_data_array.shape)
            prediction = self.lstm_model(laser_data_array)
            print("prediction: ", prediction)

            # 发送predictions到速度节点
            self.speedx = float(prediction[0][0])
            self.speedz = float(prediction[0][1])
            print("speedx: ", self.speedx,  "speedz: ", self.speedz)
            twist_msg = Twist()
            twist_msg.linear.x = self.speedx
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
