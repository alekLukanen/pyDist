from distutils.core import setup

requirements = []
with open('./requirements.txt', 'r') as file:
    for line in file.readlines():
        requirements.append(line.replace("\n", ""))

setup(
    name='pyDist',
    version='0.1.0',
    author='Aleksandr Lukanen',
    author_email='',
    packages=['pyDist'],
    url='https://github.com/alekLukanen/pyDist',
    license='LICENSE',
    description='Used to distribute Python Futures across a '
                'network of computers.',
    long_description=open('README.md').read(),
    install_requires=requirements,
)
# scripts=['bin/stowe-towels.py', 'bin/wash-towels.py'],
