"""Setup script for motofw package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")
else:
    long_description = "A Python tool for querying and downloading OTA firmware updates from Motorola's update servers"

setup(
    name="motofw",
    version="0.1.0",
    author="Motofw Contributors",
    description="A Python tool for querying and downloading OTA firmware updates from Motorola's update servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Uaemextop/motofw",
    packages=find_packages(exclude=["tests", "tests.*", "source_code", "source_code.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "urllib3>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "motofw=motofw.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
