import os

from setuptools import find_packages, setup

dir_path = os.path.dirname(__file__)

readme_file = 'README.md'
readme_path = os.path.join(dir_path, readme_file)
with open(readme_path, 'r') as file:
    long_description = file.read()

requirements_file = 'requirements.txt'
requirements_path = os.path.join(dir_path, requirements_file)
with open(requirements_path, 'r') as file:
    requirements = [line.removesuffix('\n') for line in file.readlines()]

setup(
    name='discmos',
    version='0.0.1',
    description='Generates a mosaic of Discord emojis that matches an image',
    long_description=long_description,
    python_requires='>=3.10',
    packages=find_packages(),
    entry_points={'console_scripts': ['discmos = discmos.cli:cli']},
    install_requires=requirements,
    classifiers=[],
)
