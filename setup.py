from setuptools import setup, find_packages
from google.analytics.measurement_protocol import __name__ as gamp_name, __author__ as gamp_author, __license__ as gamp_license, __version__ as gamp_version

setup(
    name=gamp_name,
    version=gamp_version,
    description='Send hits to Google Analytics through its Measurement Protocol API.',
    long_description=open('README.md').read(),
    author=gamp_author,
    author_email='yuhuibc@gmail.com',
    packages=find_packages(),
    install_requires=['requests>=2.0,<3.0a0'],
    license=gamp_license,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms=['any'],
)
