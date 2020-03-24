EMeRGE [![](https://img.shields.io/github/downloads/nrel/emerge/total.svg?colorB=FF7300)]()
===================================================================================================

EMeRGE (Emerging technologies Management and Risk evaluation on distribution Grids Evolution) is a collection of mini-tools to help users develop openDSS feeder model from GIS (.shp) file and perform risk analysis at various PV scenarios and visulize results in an interactive dashboard made using Dash.

## Releases [![](https://img.shields.io/github/release/NREL/emerge.svg?colorB=FF7300)](https://github.com/NREL/emerge/releases/latest)

## Installation

Run the following command to instal:

```python
pip install EMeRGE
```

## Documentation

Please visit https://nrel.github.io/EMeRGE/ for more elaborate documentation.

## Usage

```python

# Convert CSV files into Standard CSVs that can be used for developing OpenDSS files
from CSVformatter import pyCSVformatter as converter
converter.CSVFormatter(settingtomlfile)

# Convert Standard CSVs into OpenDSS files
from CSV2DSS import DSSconverter
DSSconverter.csv2dss(settingstomlfile)

# Perform Risk Analysis
from DSSRiskAnalyzer import pyRisk
pyRisk.RunRiskAnalysis(settingstomlfile)

# Combine monthly results into yearly
from CombineMonthlyResults import Monthly2Yearly
Monthly2Yearly.Monthly2Yearly(inputpath,outputpath,DonotReadFilesList)

# Results into Dashboard
from ResultDashboard import dashboard
dashboard.DashApp(settingstomlfile)

# Creating template for each of above operation is now much easier
from Result.Dashboard import dashboard
dashboard.Template(FolderPath, FeederName)



