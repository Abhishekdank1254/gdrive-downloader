from setuptools import setup, find_packages

setup(
    name="gdrive-downloader",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client",
        "google-auth-oauthlib",
        "google-auth-httplib2"
    ],
    author="Abhishek",
    description="A tool to download files from Google Drive",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Abhishekdank1254/gdrive-downloader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)