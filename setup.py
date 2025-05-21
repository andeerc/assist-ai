from setuptools import setup, find_packages

setup(
    name="assist-ai",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'assist-ai=main:main',
        ],
    },
)