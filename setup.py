from setuptools import setup, find_packages

setup(
  name='Python SFDX Toolkit',
  version='0.0.3',
  description='Python SFDX Toolkit',
  license='MIT',
  author='Luca Napoletano',
  author_email='lnapo94@gmail.com',
  python_requires='>=3.9',
  packages=find_packages(),
  install_requires=[
    'click==8.1.3',
    'requests==2.27.1',
    'yaspin==2.1.0',
    'beautifulsoup4==4.11.1',
    'lxml==4.8.0',
    'xmltodict==0.13.0'
  ],
  entry_points={
    'console_scripts': [
      'pydx=pydx.pydx:main',
    ],
  },
)