from setuptools import setup, find_packages
setup(
    name='mimic',
    version="0.0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mimic=mimic:main',
        ],
    },
)
