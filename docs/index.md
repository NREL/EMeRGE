# Emerge

<p align="center"> 
<img src="images/logo.svg" width="150" style="display:flex;justify-content:center;">
<p align="center">Modern tool for exploring and performing DER impact assessment for power distribution networks. </p>
</p>

![GitHub all releases](https://img.shields.io/github/downloads/NREL/emerge/total?logo=Github&logoColor=%2300ff00&style=flat-square)
![GitHub repo size](https://img.shields.io/github/repo-size/nrel/emerge?style=flat-square)
![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/nrel/emerge?color=%23ff0000&logo=python&logoColor=%2300ff00&style=flat-square)
[![GitHub license](https://img.shields.io/github/license/NREL/emerge?style=flat-square)](https://github.com/NREL/emerge/blob/main/LICENSE.txt)
[![GitHub issues](https://img.shields.io/github/issues/NREL/emerge?style=flat-square)](https://github.com/NREL/emerge/issues)
![GitHub top language](https://img.shields.io/github/languages/top/nrel/emerge?style=flat-square)


---
## Installation Instruction

In order to use EMERGE you would need to install two softwares [python (>3.9)](https://www.python.org/) and latest stable version of [Node](https://nodejs.org/en/). Assuming both of them are already installed. You can follow following steps. 

=== "Python backend"

    <p style="font-size:15px;">The commands below should work if you are using windows command prompt. However
    if you are using mac or linux you would need to slightly adjust the 
    command to activate environment use `source env/bin/activate` instead of 
    `env\Scripts\activate.bat` everything else should work in all OS platforms. 
    Here is a link where you can read more about creating virtual environment in python
    https://docs.python.org/3/library/venv.html . </p>

    ``` cmd
    mkdir emerge_test
    cd mkdir_test
    python3 -m venv env
    env\Scripts\activate.bat
    git clone https://github.com/NREL/emerge.git
    cd emerge
    pip install -e.
    ```

=== "Vue front end"

    <p style="font-size:15px;"> Assuming your current directory points to root of cloned emerge repositoty you can run the following commands to install npm dependencies. </p>

    ```cmd
    cd emerge/emerge_web
    npm install
    ```

