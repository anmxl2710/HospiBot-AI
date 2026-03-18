from setuptools import setup, find_packages

package_name = 'hospital_task_manager'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/hospital_system.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='medhavi',
    maintainer_email='medhavi@example.com',
    description='Hospital robot task allocation system',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'main_controller = hospital_task_manager.main_controller:main',
            'task_manager = hospital_task_manager.task_manager:main',
            'client_node = hospital_task_manager.client_node:main',
        ],
    },
)
