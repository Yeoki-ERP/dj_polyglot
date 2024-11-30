from setuptools import setup, find_packages

setup(
    name="dj_polyglot",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2",
        "polib>=1.2.0",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
    ],
)