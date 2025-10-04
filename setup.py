from pathlib import Path

from setuptools import find_namespace_packages, setup

# Load packages from requirements.txt
BASE_DIR = Path(__file__).parent
with open(Path(BASE_DIR, "requirements.txt")) as file:
    required_packages = [ln.strip() for ln in file.readlines()]

# Define our package
setup(
    name="EduGPT",
    version=0.1,
    description="AI instructor using LLMs and Langchain with MCP Tools",
    author="Shail",
    author_email="shailgiri9@gmail.com",
    url="https://github.com/shail0iri/EduGPT",
    python_requires=">=3.10",
    packages=find_namespace_packages(),
    install_requires=required_packages,
    extras_require={
        "dev": ["pre-commit==2.19.0"],
    },
   classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

