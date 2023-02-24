from setuptools import setup, find_packages

setup(
    name="s3docs-upload",
    version='0.1.0',
    url='https://github.com/bkief/mkdocs-builder',
    install_requires=[
        'boto3',
    ],
    license='MIT',
    description='Util for uploading Mkdocs site to S3',
    packages=find_packages(),
    include_package_data=True
)
