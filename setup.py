from distutils.core import setup
setup(name='folia2alpino',
      version='0.1',
      description='Converts FoLiA files to Alpino XML files',
      url='https://github.com/UUDigitalHumanitieslab/folia2alpino',
      author='Digital Humanities Lab, Utrecht University',
      author_email='dh.developers@uu.nl',
      license='MIT',
      packages=['folia2alpino'],
      install_requires=['argparse', 'PyNLPl'],
      python_requires='>=3.6',
      zip_safe=True,
      entry_points={
          'console_scripts': [
              'folia2alpino = folia2alpino.__main__:main'
          ]
      })
