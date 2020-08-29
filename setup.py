import re
from setuptools import setup

# get version number
with open('canvasaio/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(),
        re.MULTILINE
    ).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='canvasaio',
    version=version,
    description='Port of canvasapi by UCF to asyncio',
    url='https://github.com/spapadim/canvasaio',
    author_email='spapadim@gmail.com',
    license='MIT License',
    packages=['canvasaio'],
    include_package_data=True,
    install_requires=['pytz', 'requests'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
    ],
)
