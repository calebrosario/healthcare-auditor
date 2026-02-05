from setuptools import setup
from setuptools import find_packages

setup(
    name="healthcare-auditor-backend",
    version="0.1.0",
    description="Healthcare billing fraud detection and compliance verification system",
    packages=find_packages(),
    python_requires=">=3.11",
)
