from distutils.core import setup
setup(name='corpus2alpino',
      version='0.1.4',
      description='Converts FoLiA and TEI files to Alpino XML files',
      url='https://github.com/UUDigitalHumanitieslab/folia2alpino',
      author='Digital Humanities Lab, Utrecht University',
      author_email='dh.developers@uu.nl',
      license='MIT',
      packages=['corpus2alpino'],
      install_requires=['argparse', 'PyNLPl', 'python-ucto', 'tei-reader'],
      python_requires='>=3.6',
      zip_safe=True,
      entry_points={
          'console_scripts': [
              'corpus2alpino = corpus2alpino.__main__:main'
          ]
      })
