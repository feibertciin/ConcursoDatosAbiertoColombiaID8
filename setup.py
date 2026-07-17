from setuptools import setup, find_packages

setup(
    name="framework-ml-snies",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Dependencies managed via requirements.txt
    ],
    entry_points={
        "console_scripts": [
            "framework-ml-cli=src.interfaces.cli:main",
        ],
    },
)
