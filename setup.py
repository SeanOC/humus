from setuptools import setup, find_packages

setup(
    name='Humus',
    version='0.1.0',
    packages=find_packages(),#['humus',],
    entry_points = {
        'console_scripts': [
            'humus = humus.commands:humus_sync',
        ],
    },
    license='MIT',
    long_description=open('README.rst').read(),
)