==================
Installation Guide
==================

EMeRGE can be installed via pip command:

.. code-block:: python

	pip install emerge
	
Alternately, you can clone git repo from https://github.com/nrel/emerge , and use the following commands to build the module and install it.

.. code-block:: python

	python setup.py -build
	python setup.py -install

Preferred way is to create virtual environment and install EMeRGE there. If you have anaconda installed please follow these steps:

.. code-block:: python

    conda create -n my_env python=3.7
    conda activate my_env
    pip install emerge

You can select this virtual environment in your code-editor.

If you are using Visual Studio: Goto View>>Command Palette>>Python: Select Interpretor, scroll down untill you see my_env environment and click it.

! Awesome you have sucessfully set up EMeRGE in your machine.