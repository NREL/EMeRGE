from setuptools import setup, find_packages

with open("README.md","r") as fh:
    long_description = fh.read()

setup(
    name='EMeRGE',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='v1.2-alpha',
    description='Emerging technologies Management and Risk evaluation on distributions Grid Evolution',
    author='Kapil Duwadi',
    author_email='kapil.duwadi@nrel.gov',
    packages=find_packages("EMeRGE"),
    url="https://github.com/NREL/EMeRGE",
    keywords="Distribution System DER technologies management risk impact analysis",
    install_requires=["pyproj==1.9.6",
                    "dash_html_components==1.0.2",
                    "numpy==1.16.4",
                    "networkx==2.3",
                    "pandas==0.24.2",
                    "plotly==4.4.1",
                    "dash_daq==0.3.3",
                    "dash_core_components==1.8.0",
                    "OpenDSSDirect.py==0.3.7",
                    "toml==0.10.0",
                    "dash==1.9.0",
                    "dash_table==4.6.0",
                    "matplotlib==3.1.0"],
    package_dir={"": "EMeRGE"},   
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent"
    ]
)