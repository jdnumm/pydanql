from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='gamma-kit',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'psycopg2-binary',
        'pydantic'
    ],
    author='Johannes Daniel Nümm',
    author_email='code@blacktre.es',
    description='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://blacktre.es',
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Topic :: Utilities'
    ],
    py_modules=['gamma']
)
