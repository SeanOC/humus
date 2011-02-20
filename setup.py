from setuptools import setup, find_packages

setup(
    name='Humus',
    version='0.1.3',
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'humus = humus.commands:humus_sync',
        ],
    },
    license='MIT',
    long_description=open('README.rst').read(),
    install_requires=['boto>=2.0b4'],
    author = "Sean O'Connor",
    author_email = "sean@saaspire.com",
    description = "A simple S3 backup script",
    keywords = "amazon aws s3 backup",
    url = "https://github.com/SeanOC/humus",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Archiving :: Backup',
    ],
)