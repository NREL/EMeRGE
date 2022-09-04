1. Fork the repo located at `https://github.com/NREL/emerge`
 
2. Clone the forked repo in your local setup
   
    ```git
    git clone https://github.com/<YourUserName>/emerge
    ```

3. Create the branch following naming convention `feature\<feature_name>` by executing the command

    ```git
    git checkout -b feature\<feature-name>
    ```

4. If you need instructions to create the environment please refer to the Welcome page.

5. Make your changes
6. Make sure to write tests in a proper file, create new file as necessary. Convention is to have single test file for each module. 
   
7. Execute the test and make sure all of them pass.

    ```python
    cd <cloned_repo>
    pytest -p no:faulthandler
    ```

8. Make sure your code has passed linting test and black test. Use the following commands for checking linting and formatting.
   
    ```
    pip install pylint
    cd <cloned_directory>
    pylint shift
    pip install black
    black --check --line-length 80 shift
    ```

9.  Make sure you are following [Googles docstring guidlines](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) when documenting classes, methods, functions, modules and packages.

10. In order to update the documentation page please make your changes inside `docs/` folder and to view the changes run the following command.

    ```cli
    cd <cloned_repo>
    mkdocs serve
    ```