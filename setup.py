from distutils.core import setup
setup(name='corpus2alpino',
      version='0.1.6',
      description='Converts FoLiA and TEI files to Alpino XML files',
      url='https://github.com/UUDigitalHumanitieslab/corpus2alpino',
      author='Sheean Spoel, Digital Humanities Lab, Utrecht University',
      author_email='s.j.j.spoel@uu.nl',
      license='MIT',
      packages=['corpus2alpino'],
      install_requires=['argparse', 'Cython', 'PyNLPl', 'python-ucto', 'tei-reader'],
      python_requires='>=3.6',
      zip_safe=True,
      entry_points={
          'console_scripts': [
              'corpus2alpino = corpus2alpino.__main__:main'
          ]
      })
