from setuptools import setup

setup(
    name='audiobooker',
    version='0.1.1',
    packages=['audiobooker', 'audiobooker.scrappers'],
    install_requires=["requests", "bs4", "feedparser"],
    url='https://github.com/JarbasAl/audiobooker',
    license='MIT',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    description='audio book scrapper'
)
