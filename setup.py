from setuptools import setup

# Read the contents of the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='contextS',
    version='1.0.0',
    author='Jules for ProCreations',
    description='ContextS MCP Server and CLI tool with AI model fallback.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    py_modules=['main'],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'contextS = main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
