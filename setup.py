from setuptools import setup

setup(
    name='audiobooker',
    version='0.5.0',
    packages=['audiobooker', 'audiobooker.scrappers'],
    install_requires=["requests", "bs4", "feedparser", "rapidfuzz",
                      "requests-cache", "site-map-parser"],
    url='https://github.com/OpenJarbas/audiobooker',
    license='MIT',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    description='audio book scrapper'
)
