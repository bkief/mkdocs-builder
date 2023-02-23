from setuptools import setup, find_packages

setup(
    name='S3Docs-Upload',
    version='0.1.0',
    packages=find_packages(include=['s3docs-upload']),
    install_requires=[
        'boto3',
    ]
)
