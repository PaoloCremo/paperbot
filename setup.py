from setuptools import setup, find_packages

setup(
    name="pepfindbot",
    version="1.2.1",
    author="Paolo Cremonese",
    author_email="cremonesep25@gmail.com",
    description="A package to find ArXiv papers and send results via Telegram",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/PaoloCremo/paperbot",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "telegram-send",
        "beautifulsoup4",
        "matplotlib",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
)