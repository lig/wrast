import sys

from setuptools import find_packages, setup


setup(
    name='wrast',
    use_scm_version=True,
    description='Python Code Reformatter.',
    url='https://github.com/lig/wrast',
    author='Serge Matveenko',
    author_email='s@matveenko.ru',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    keywords='code formatter python ast pep8',
    packages=find_packages(),
    setup_requires=['setuptools_scm'],
    install_requires=['click'],
    extras_require={
        'test': ['tox'],
    },
    entry_points={
        'console_scripts': [
            'wrast=wrast.cli:main',
        ],
    },
)
