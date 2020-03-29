from setuptools import setup

setup(
    name='audiobooker',
    version='0.2.7',
    packages=['audiobooker', 'audiobooker.scrappers', 'audiobooker.utils'],
    install_requires=["requests", "bs4", "feedparser", "rapidfuzz"],
    url='https://github.com/OpenJarbas/audiobooker',
    license='MIT',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    description='audio book scrapper'
)
