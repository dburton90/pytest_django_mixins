from setuptools import setup


setup(name="pytest_django_mixins",
      version=0.1,
      description='Provide mixins for testing django apps with pytest.',
      long_description='Mixins prepare easy extandable tests for basic django tasks (views - permissions, post data, get data, ...)',
      url="https://github.com/dburton90/pytest_django_mixins.git",
      author="Daniel Bartoň",
      author_email='daniel.barton@seznam.cz',
      license='GPLv3',
      packages=['pytest_django_mixins'],
      install_requires=[
          'pytest',
          'pytest_matrix'
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Plugins',
          'Framework :: Pytest',
          'Topic :: Software Development :: Testing',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Software Development :: Libraries',
      ],
      keywords='pytest mixin pytest_matrix django pytest_django_mixins generating tests',
      zip_safe=False,
      entry_points={'pytest11': ['django_mixins = pytest_django_mixins.plugin']}
      )
