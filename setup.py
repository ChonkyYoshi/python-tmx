from setuptools import setup, find_packages

setup(
    name="python-tmx",
    version="0.1.2",
    author="Enzo Agosta",
    author_email="agosta.enzowork@gmail.com",
    description="Python library for manipulating tmx files",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
