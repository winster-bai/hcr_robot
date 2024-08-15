# 基本介绍
本项目使用ros2 humble框架搭建，用于简单机器人虚拟环境仿真，可以用于采集数据、训练模型  

# 环境配置
## 1.下载ROS2 Humble  
下载以及基础操作教程：  
[https://docs.ros.org/en/humble/index.html](https://docs.ros.org/en/humble/index.html)   

## 2.安装Gazebo
略  

## 3.下载仓库  
`mkdir ~/dev_ws`
`cd dev_ws`
`git clone https://github.com/winster-bai/ros2_humble_simulation.git`
`colcon build`

# 节点及功能

## 1. HCR底座的URDF模型

模型路径： `/home/dfrobot/dev_ws/src/hcr_robot/urdf/hcr_with_camera_laser_gazebo.xacro`

## 2. 使用rviz直接查看修改后的模型用于debug 

```bash
ros2 launch hcr_robot display_xacro.launch.py
```

也可以启动gazebo后在rviz里 `add robot model`

## 3. gazebo中调用上面的模型

### 调用RGB摄像头&激光雷达

```bash
ros2 launch hcr_robot load_hcr_camera_laser_into_gazebo.launch.py
```

如果需要别的机器运行，需要 `export GAZEBO_MODEL_PATH=$(pwd)/models` 来加载world模型

### 调用深度摄像头（也可以返回图像信息）

```bash
ros2 launch hcr_robot load_hcr_depthcamera_into_gazebo.launch.py
```

**需要修改world**，现在用的是开源室内模型

![图片](image/rviz1.png)

## 4. rviz中显示

```bash
ros2 run rviz2 rviz2
```

配置文件（rviz中保存）可以加在后面，如：

```bash
ros2 run rviz2 rviz2 -d /home/dfrobot/dev_ws/src/hcr_robot/config/hcr_slam_tool.rviz
```

## 5. 键盘控制移动机器人

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**可以改成手柄或其他，手柄参考youtube代码**

## 6. yolo

订阅 `camera/image_raw` 并调用yolov8nano，识别精度较低，可能能需按照识别目标针对性定制

```bash
ros2 run yolobot_recognition yolov8_ros2_pt.py
```

暂时无法在飞书文档外展示此内容

## 7. slam_toolbox地图数据发布

(绘制完成后在yaml文件中更改需要调取的地图文件)  
每次nav2导航之前都要启动slam发布map  
**地图绘制也可以用这个，从空白地图开始绘制需要修改.yaml文件中的`mode=mapping`**

```bash
ros2 launch slam_toolbox online_async_launch.py slam_params_file:=/home/dfrobot/dev_ws/src/hcr_robot/config/mapper_params_online_async.yaml use_sim_time:=true
```

扫描后点击rviz中 `panels-add new panel-slamtoolboxplugin`，点击 `save map`（保存为pgm和yaml文件）或者 `serialize map`（可以在rviz中继续倒入该地图继续扫描，修改上面yaml文件中的mode和map_file_name）

## 8. nav2路径规划

```bash
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true
```

### 本地替换方案

用本地地图

```bash
ros2 launch nav2_bringup localization_launch.py map:=/home/dfrobot/dev_ws/src/hcr_robot/map/hcr_map_save.yaml use_sim_time:=true
```

然后启动nav2

```bash
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true map_subscribe_transient_local:=true
```

此方法会实时更新costmap  
瞬态本地订阅

用launch调用map server和amcl

```bash
ros2 launch hcr_robot localization_launch.py map:=/home/dfrobot/dev_ws/src/hcr_robot/map/hcr_map_save.yaml use_sim_time:=true
```

记得rviz中点击 `map-topic-durability` 为 `transient local`  
同样用瞬态本地方法启动nav2

```bash
ros2 launch hcr_robot navigation_launch.py use_sim_time:=true map_subscribe_transient_local:=true
```

本地化可以实时更新代价地图，需要把nav的一些launch file 复制到本地，并修改参数，具体见视频  
[https://www.youtube.com/watch?v=jkoGkAd0GYk&t=734s](https://www.youtube.com/watch?v=jkoGkAd0GYk&t=734s)

## 9. 查询设置当前位置

```bash
ros2 topic echo /odom
```

### 厨房

```
pose:
  pose:
    position:
      x: 7.385820849502236
      y: -3.67132739701038
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: -0.5752126224546109
      w: 0.8180039357905861
```

### 卧室

```
pose:
  pose:
    position:
      x: -4.262302802783025
      y: -0.0558546427720895
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: 0.987924605366016
      w: 0.1549353868953168
```

### 浴室（健身房）

```
pose:
  pose:
    position:
      x: 1.6530433964811797
      y: 4.237551605454772
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: 0.24494699612691187
      w: 0.969536471252321
```

## 10. 通过命令行设置机器人目标点

(在rosgpt里有写位置发布，改下节点名就行)

```bash
ros2 topic pub /goal_pose geometry_msgs/msg/PoseStamped "{header: {stamp: {sec: 0, nanosec: 0}, frame_id: 'map'}, pose: {position: {x: 7.38, y: -3.67, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: -0.57, w: 0.81}}}" -r 1
```

## 11. 修改ros gpt代码实现最终效果

依次打开gazebo、rviz、slam、nav2、rosgpt_client、rosnode以及rosnav2

```bash
source rosgpt/install/setup.bash
ros2 run ... # 后续把node封装成launch/bring up
```


## 12. GPT4Vision

获取 `camera/image_raw` 图像数据并发布到gpt4v获取回复  
回复格式 `{"location": "bedroom", "object": "bed, nightstand, trash can", "odom": [-3.4640721060500312, -0.1990534521504475, -0.9691540916705709, -0.24645556718846304]}`  
odom内四个数字为当前机器人在odom坐标系的位置以及方向

```bash
ros2 run hcr_robot gpt4v_test
```
