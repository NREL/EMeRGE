=================
Monthly to Yearly 
=================

The package `CombineMonthlyResults` allows combining CSV files from all 12 month results into aggregated CSV files representing result of whole year.
This package was developed by keeping in mind that running simulation for whole year in a laptop user might run into memory issues. In that case, user
can perform simulation on month-by-month basis and use this package to combine results. 


.. autoclass:: CombineMonthlyResults.Monthly2Yearly.Monthly2Yearly
   :members:
   :undoc-members:
   :show-inheritance:


The class ``Monthly2Yearly`` is located inside package CombineMonthlyResults in the Monthly2Yearly module within 'EMeRGE' tool.
Now, before using this class, you need to the setup the folder in a format this class would understand.
In order to make this process easy, you can first call the template class:

.. autoclass:: CombineMonthlyResults.Monthly2Yearly.Template
   :members:
   :undoc-members:
   :show-inheritance:
