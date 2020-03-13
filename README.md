EMeRGE [![](https://img.shields.io/github/downloads/nrel/emerge/total.svg?colorB=FF7300)]()
===================================================================================================

EMeRGE (Emerging technologies Management and Risk evaluation on distribution Grids Evolution) is a collection of mini-tools to help users develop openDSS feeder model from GIS (.shp) file and perform risk analysis at various PV scenarios and visulize results in an interactive dashboard made using Dash.

## Releases [![](https://img.shields.io/github/release/NREL/emerge.svg?colorB=FF7300)](https://github.com/NREL/emerge/releases/latest)

## Installation

Run the following command to instal:

```python
pip install EMeRGE
```

## Usage

```python
from EMeRGE import CSVformatter.pyCSVformatter as converter

# Convert normal CSVs into Standars CSVs which can be used for developing OpenDSS models

converter.CSVFormatter(settingtomlfile)



