from setuptools import setup, find_packages
import sys

version = '0.1.1'

entry_points = {
    'ckan.plugins': [
        "api_ng = ckanext.api_ng.plugin:ApiNgPlugin",
    ],
}

install_requires = []
if sys.version_info < (2, 7):
    install_requires.append('ordereddict')

setup(
    name='ckanext-api-ng',
    version=version,
    description="New-generation API for Ckan",
    long_description="New-generation API for Ckan",
    author="Samuele Santi",
    author_email="samuele.santi@trentorise.eu",
    url='http://rshk.github.io/ckan-api-ng',
    license='Affero GPL',
    classifiers=[],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.api_ng'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points=entry_points,
)
