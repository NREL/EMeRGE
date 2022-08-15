from setuptools import setup, find_packages

with open("README.md","r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='emerge',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='v2.0.0-alpha',
    description='Emerging technologies Management and Risk evaluation on distributions Grid Evolution',
    author='Kapil Duwadi',
    author_email='kapil.duwadi@nrel.gov',
    packages=find_packages("src"),
    # package_data={".//dssdashboard//assets":["*.css","*.png"]},
    url="https://github.com/NREL/EMeRGE",
    keywords="Distribution System DER technologies management risk impact analysis",
    install_requires=requirements,
    package_dir={"emerge": "emerge"}, 
    entry_points={
        "console_scripts": [
            "emerge=emerge.cli.cli:cli"
        ],
    },
    python_requires=">=3.9",  
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ]
)