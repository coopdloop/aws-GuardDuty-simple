# setup.py
from setuptools import setup, find_packages

setup(
    name="security_monitor",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "boto3>=1.26.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
)

# src/security_monitor/__init__.py
# Leave this empty or add version info:
__version__ = "0.1"
