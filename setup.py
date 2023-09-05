from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pydanql',
    version='0.24-alpha',
    packages=find_packages(),
    install_requires=[
        'psycopg2>=2.9.0',
        'pydantic>=2.3.0',
        'inflect>=7.0.0'
    ],
    author='Daniel Nümm',
    author_email='pydanql@blacktre.es',
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
    py_modules=['pydanql']
)
