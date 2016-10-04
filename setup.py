from setuptools import setup

with open('README.rst') as f:
    README = f.read()

setup(
    name='rr',
    version='0.0.1',
    description='Runner-Reloader for development',
    long_description=README,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    author='Alexander Zelenyak',
    author_email='zzz.sochi@gmail.com',
    url='https://github.com/zzzsochi/rr',
    keywords=['runner', 'reload', 'develop'],
    packages=['rr'],
    install_requires=['colorama'],
    entry_points={
        'console_scripts': [
            'rr = rr.__main__:main',
        ],
    },
)
