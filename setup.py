"""
CodeSnippetBank Setup Script
Install tissue CLI and runtime components
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='codebank',
    version='1.0.0',
    author='CodeSnippetBank Team',
    author_email='team@codebank.ai',
    description='Revolutionary Edge AI code generation system',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/codebase/codebank',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy>=1.19.0',
        'scikit-learn>=0.24.0',
        'nltk>=3.6.0',
        'Pillow>=8.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.9',
        ],
        'edge': [
            'micropython-unix-stubs>=1.13',
        ],
    },
    entry_points={
        'console_scripts': [
            'tissue=tools.tissue_cli:main',
            'codebank=tools.tissue_cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'codebank': [
            'tissues/cv/*.py',
            'tissues/nlp/*.py',
            'tissues/ml/*.py',
            'framework/quality/*.py',
            'framework/composition/*.py',
            'framework/versioning/*.py',
            'api/*.py',
            'tools/*.py',
        ],
    },
)