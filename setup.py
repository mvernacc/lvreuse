import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(name='Strategies for Re-use of Launch Vehicle First Stages',
      version='0.0',
      description='Analysis of partially reusable launch vehicle cost & performance in Python',
      author='Matthew Vernacchia and Kelly Mathesius',
      author_email='mvernacc@mit.edu',
      license='',    # TODO
      url='',    # TODO
      packages=['lvreuse'],
      install_requires=['numpy', 'seaborn', 'matplotlib', 'rhodium'],
      classifiers=[
          'Development Status :: 1 - Planning',
          'Environment :: Console',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 3',
          'Natural Language :: English',
          'Topic :: Scientific/Engineering',
          ],
     )
