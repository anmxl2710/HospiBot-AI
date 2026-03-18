from setuptools import setup

package_name = 'hospital_fleet_manager'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='medhavi',
    maintainer_email='medhavi@todo.todo',
    description='Fleet manager node for hospital robots',
    license='MIT',
    entry_points={
        'console_scripts': [
            'fleet_manager = hospital_fleet_manager.fleet_manager:main',
        ],
    },
)
