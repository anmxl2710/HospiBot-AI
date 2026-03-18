from setuptools import setup
import os
from glob import glob

package_name = 'hospital_task_manager'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='medhavi',
    maintainer_email='medhavi@todo.todo',
    description='Hospital auction-based task manager',
    license='MIT',
    entry_points={
        'console_scripts': [
            'task_manager = hospital_task_manager.task_manager:main',
            'client_node  = hospital_task_manager.client_node:main',
        ],
    },
)
