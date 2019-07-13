import setuptools
import codecs

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name='eecalpy',
      version='0.9.0',
      description='collection of classes for simple to complex electrical calculations',
      long_description=long_description,
      url='http://github.com/wese3112/eecalpy.git',
      author='Sebastian Werner',
      author_email='wese3112@startmail.com',
      packages=setuptools.find_packages(),
      install_requires=[
          'lark-parser',
      ],
      # scripts=['bin/eecalpy.cmd'],
      entry_points={
          'console_scripts': [
              'eecalpy = eecalpy.__main__:main'
          ]
      },
      zip_safe=False,
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent",
      ],
)
