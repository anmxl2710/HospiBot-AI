from setuptools import find_packages, setup

package_name = 'hospital_robot_sim'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='anmol',
    maintainer_email='anmol@todo.todo',
    description='Hospital Gazebo Classic simulation with autonomous robots (ROS 2 Humble).',
    license='MIT',
)

