#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from nav_msgs.msg import Odometry


# openai requires the image to be base64 encoded
import base64
import requests
import json

# OpenAI API Key
api_key = "your_api_key"

class ImageSubscriber(Node):
    def __init__(self):
        super().__init__('image_subscriber')
        self.sub = self.create_subscription(Image, 'camera/image_raw', self.listener_callback, 10)
        self.pose_subscriber = self.create_subscription(Odometry, "/odom", self.pose_callback, 10)
        self.x = 0.0
        self.y  = 0.0
        self.z  = 0.0
        self.w  = 0.0
        self.pose = Odometry()
        self.cv_bridge = CvBridge()
        # self.image_received = False  # 添加一个标志，用于判断是否已经接收到图像数据

    def pose_callback(self, msg):
        # self.x = msg.x
        # self.y  = msg.y
        # self.theta  = msg.theta
        # self.pose = msg

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.z = msg.pose.pose.orientation.z
        self.w = msg.pose.pose.orientation.w
        self.pose = msg
        
        print (self.z) #used for debegging

    def listener_callback(self, data):
        key = input("Press 'i' to receive image: ")
        if key == 'i':  # 如果按下了'i'键
            self.get_logger().info('Receiving video frame')
            image = self.cv_bridge.imgmsg_to_cv2(data, 'bgr8')
            cv2.imwrite('image.jpg', image)  # 将图像保存为JPEG文件
            self.get_logger().info('image saved as image.jpg')
            # self.image_received = True  # 标记已经接收到图像数据
            
            # 发送到openai
            # Function to encode the image
            def encode_image(image_path):
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            image_path = "image.jpg"# Path to your image
            base64_image = encode_image(image_path)
            headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
            }

            prompt = '''You will be given picture of a house, and you need to return a JSON conformant to the ontology. Any action not in the ontology must be ignored. The ontology is as follows:
            {"location":"string","object":"string"}
            Here is some example JSON:
            {"location":"kitchen","object":"table, fride, trash can"}
            {"location":"bathroom","object":"toilet, sink, shower"}
            {"location":"bedroom","object":"bed, nightstand, lamp"}
            note: the object field can have multiple objects separated by commas, but should not more than 3 objects.
            location can be kitchen, bathroom and bedroom, don't generate other locations.
            '''
            payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": prompt
                    },
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                    }
                ]
                }
            ],
            "max_tokens": 300
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            #print(response.json())
            # Extract the content field from the response
            content_str = response.json()["choices"][0]["message"]["content"]
            content = json.loads(content_str)
            print("content", content)
            
            odom = [self.x, self.y, self.z, self.w]
            content["odom"] = odom
            print("content2:", content)
            
            # Save the content to a JSON file
            with open("house_location.json", "a") as file:
                json.dump(content, file)


def main(args=None):
    rclpy.init(args=args)
    node = ImageSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

