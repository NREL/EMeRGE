=====================
CSV to DSS conversion
=====================

In this page, I am going to show how to convert standard csv files containing distribution data into .dss files which 
can be used to perform distribution system analysis. Standard csv files are csv files generated using class ``CSVFormatter``.
Let's see the description of the class you would use for for this conversion. 

.. autoclass:: CSV2DSS.DSSconverter.csv2dss
   :members:
   :undoc-members:
   :show-inheritance:


The class ``csv2dss`` is located inside package CSV2DSS in the DSSconverter module within 'EMeRGE' tool.
Now, before using this class, you need to the setup the folder in a format this class would understand.
In order to make this process easy, you can first call the template class:

.. autoclass:: CSV2DSS.DSSconverter.Template
   :members:
   :undoc-members:
   :show-inheritance:
