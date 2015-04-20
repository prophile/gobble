from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = f.read()


setup(name='gobble',
      version='0.1.0',
      packages=find_packages(),
      description='A simpler parsing framework',
      long_description=long_description,
      author='Alistair Lynn',
      author_email='alistair@alynn.co.uk',
      url='https://github.com/prophile/gobble',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Text Processing',
      ],
      setup_requires=[
        'nose >=1.3, <2'
      ],
      tests_require=[
        'coverage >=3.7, <4'
      ])
