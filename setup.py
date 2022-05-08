from setuptools import setup, find_packages

setup(
  name='pydx',
  version='0.13',
  description='Python SFDX Toolkit',
  license='MIT',
  author='Luca Napoletano',
  author_email='lnapo94@gmail.com',
  packages=['src'],
  python_requires='>=3.09',
  entry_points = {
    'console_scripts': ['pydx = src.pydx:main'],
  }
)