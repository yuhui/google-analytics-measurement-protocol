from setuptools import setup, find_packages

setup(
    name='google-analytics-measurement-protocol',
    version='0.2dev1',
    description='Send hits to Google Analytics through its Measurement Protocol API.',
    long_description=open('README.md').read(),
    author='Yu Hui',
    author_email='yuhuibc@gmail.com',
    packages=find_packages(),
    install_requires=['requests>=2.0,<3.0a0'],
    license='License :: OSI Approved :: MIT License',
    classifiers=[
        'Development Status :: 1 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms=['any'],
)
