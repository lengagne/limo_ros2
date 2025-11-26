import os
from glob import glob
from setuptools import setup, find_packages

package_name = 'limo_arena'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/worlds', ['worlds/arena.world']),
        (os.path.join( 'share', package_name, 'launch'), glob (os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Sebastien Lengagne',
    maintainer_email='lengagne@gmail.com',
    description='Package pour la gestion de l\'arène LIMO',
    license='Apache 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'referee = limo_arena.referee:main',
            'scoreboard = limo_arena.scoreboard:main',
        ],
    },
)
