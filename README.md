
## Emerging technologies Management and Risk evaluation on distribution Grids Evolution (EMERGE)


![GitHub all releases](https://img.shields.io/github/downloads/NREL/EMeRGE/total?logo=Github&logoColor=%2300ff00&style=flat-square) ![GitHub repo size](https://img.shields.io/github/repo-size/nrel/emerge?style=flat-square) ![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/nrel/EMeRGE?color=%23ff0000&logo=python&logoColor=%2300ff00&style=flat-square) [![GitHub license](https://img.shields.io/github/license/NREL/shift?style=flat-square)](https://github.com/NREL/emerge/blob/main/LICENSE.txt) [![GitHub issues](https://img.shields.io/github/issues/NREL/emerge?style=flat-square)](https://github.com/NREL/shift/issues) ![GitHub top language](https://img.shields.io/github/languages/top/nrel/emerge?style=flat-square) ![Snyk Vulnerabilities for GitHub Repo](https://img.shields.io/snyk/vulnerabilities/github/nrel/emerge?style=flat-square)

### :wave: Welcome to EMERGE Repository !

EMERGE allows user quickly analyze the distribution feeder by providing access to simple yet powerful visualization platform. You can compute metrics for both snapshot and time series simulations (note we are still actively developing new features on this so things might change rapidly. if you have any feedback reach out to us by creating issue).

:rocket: We would appreciate if you can star our repo. 

### Installation instructions

The installation process is farily easy. You can clone or download the repo and install the python package. 

If you are just planning to use the repo you can use following command. Make sure you have setup python environment either using Anaconda or barebone python virtual environment. We recommend python 3.9 for this package.

```
cd <cloned-directory>
python setup.py install
```

If you are however planning to contribute you can install using the following command.

```
cd <cloned-repository>
pip install -e .
```

Note we have not yet published this repo to PyPI so if you install from PyPI you will get the legacy version of EMERGE.


### Using the package

Once you installed the package you have access to command line utility called `emerge`. You can openup command prompt, activate your environment and type `emerge --help` which will list out all the commands available.

We have included examples folder at the root of repo for you to play with EMERGE.


First let's create the metrics. To do this let's open up command prompt, activate the environment and navigate to example folder and run the followig command.

```
emerge snapshot-metrics -m ./master.dss
```

The above code will generate db.json file in the current working directory. You can choose to store this file elsewhere with different name by providing extra flag in the command. If you need help you can use the command `emerge snapshot-metrics -m ./master.dss --help`.

Now let's run the server for the dashboard. You can use following command to run the server.

```
emerge serve -db ./db.json -p 8050
```

This will take couples of seconds to be ready and after that you can go to your browser and visit `localhost:8050`. 

:smiley: Great Job!


