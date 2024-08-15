# dfrobot hcr move robot with rgb cam and slim, include gazebo rviz functions.
from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'hcr_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    #packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'urdf'), glob(os.path.join('urdf', '*.*'))),
        (os.path.join('share', package_name, 'meshes'), glob(os.path.join('meshes', '*.*'))),
        (os.path.join('share', package_name, 'urdf/sensors'), glob(os.path.join('urdf/sensors', '*.*'))),
        (os.path.join('share', package_name, 'worlds'), glob(os.path.join('worlds', '*.*'))),   
        (os.path.join('share', package_name, 'rviz'), glob(os.path.join('rviz', '*.rviz'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dfrobot',
    maintainer_email='dfrobot@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
         'topic_webcam_sub      = hcr_robot.webcam_sub:main',
         'gpt4v_test      = hcr_robot.gpt4v_test:main',
         'laser_data      = hcr_robot.laser_data_collection:main',
            'autorun      = hcr_robot.autorun:main',
            'simple_laser_data      = hcr_robot.simple_laser_data_collection:main',

        ],
    },
)
