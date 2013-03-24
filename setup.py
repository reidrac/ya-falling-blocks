#!/usr/bin/env python
from setuptools import setup, find_packages
from useboxnet.puzzle.const import VERSION, PROJECT_DESC, PROJECT_URL

def readme():
    try:
        return open('README.rst').read()
    except:
        return ""

setup(name='ya-falling-blocks',
      version=VERSION,
      description=PROJECT_DESC,
      long_description=readme(),
      author='Juan J. Martinez',
      author_email='jjm@usebox.net',
      url=PROJECT_URL,
      license='MIT',
      install_requires=['pyglet'],
      include_package_data=True,
      zip_safe=False,
      scripts=['scripts/yafb'],
      packages=find_packages(),
      classifiers = [
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Topic :: Games/Entertainment',
        'Intended Audience :: End Users/Desktop',
        ],
      )

