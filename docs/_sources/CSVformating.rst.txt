===============
Formatting CSVs
===============

In this page, I am going to show how to format CSV files which can be later on used to develop 
.dss files representing OpenDSS feeder model. This tool was developed keeping in mind that CSVs
extracted from .shp file for a distribution systems will not be perfect and always need some kind of fixing.
This tool is way to ease that process. Let's see the description of the class you would use
for formatting .csv files after being extracted from .shp files. It is assumed that, files are extracted using QGIS.
In order to extract coordinates of line elements, MMQGIS plugin must have been used which would give two csv files (attribute and coordinates for line elements).
``gis2csv`` class can be used for automatic conversion of .shp files to .csv files.

.. autoclass:: CSVformatter.pyCSVformatter.CSVFormatter
   :members:
   :undoc-members:
   :show-inheritance:


The class ``CSVformatter`` is located inside package CSVformatter in the pyCSVformatter module within 'EMeRGE' tool.
Now, before using this class, you need to the setup the folder in a format this class would understand.
In order to make this process easy, you can first call the template class:

.. autoclass:: CSVformatter.pyCSVformatter.Template
   :members:
   :undoc-members:
   :show-inheritance:
