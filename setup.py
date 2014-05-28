from setuptools import setup

setup(
    name = "summonses",
    version = "0.1",
    author = "Kevin Wilson",
    author_email = "khwilson@gmail.com",
    description = ("Analysis of how summonses affect collisions"),
    license = "Apache2",
    keywords = "example data-analysis nyc",
    url = "https://github.com/khwilson/summonses",
    packages=['summonses'],
    long_description=open('README.rst', 'r').read(),
    install_requires=open('requirements.txt', 'r').readlines()
)
