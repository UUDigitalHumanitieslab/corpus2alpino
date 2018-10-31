from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='corpus2alpino',
      version='0.2.2',
      description='Converts FoLiA and TEI files to Alpino XML files',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/UUDigitalHumanitieslab/corpus2alpino',
      author='Sheean Spoel, Digital Humanities Lab, Utrecht University',
      author_email='s.j.j.spoel@uu.nl',
      license='MIT',
      packages=['corpus2alpino'],
      install_requires=['argparse', 'Cython', 'PyNLPl', 'python-ucto', 'tei-reader', 'tqdm'],
      python_requires='>=3.6',
      zip_safe=True,
      entry_points={
          'console_scripts': [
              'corpus2alpino = corpus2alpino.__main__:main'
          ]
      })
 