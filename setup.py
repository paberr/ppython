from setuptools import setup, find_packages
import ppython

setup(
    name='ppython',
    version=ppython.__version__,
    url='https://github.com/paberr/ppython/',
    license='MIT License',
    author='Pascal Berrang',
    install_requires=[],
    author_email='spam@paberr.net',
    description='An interactive python3 interpreter with pretty syntax highlighting. Also allows to preload history files.',
    packages=find_packages(),
    include_package_data=True,
    platforms='any'
)