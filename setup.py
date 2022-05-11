from setuptools import setup

setup(
  name='pydx',
  version='0.20',
  description='Python SFDX Toolkit',
  license='MIT',
  author='Luca Napoletano',
  author_email='lnapo94@gmail.com',
  python_requires='>=3.10',
  install_requires=[
    'click',
  ],
  entry_points={
    'console_scripts': [
      'pydx=pydx:main',
    ],
  },
)