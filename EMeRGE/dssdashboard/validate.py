# Standdard libraries
import os

# Internal libraries
from dssdashboard.constants import FOLDER_LIST


""" function to validate input for dashboard """

def folder_validate(working_folder=''):

    if os.path.exists(working_folder):

        # Check all folder exists
        folders = list(os.listdir(working_folder))
        if not set(FOLDER_LIST).issubset(set(folders)):
            return f"At least one of the folder in the list {','.join(FOLDER_LIST)} is missing !!!"
        
        else:
            return 'sucess on validation !'

    else:
        raise ValueError(f'{working_folder} does not exist !!!')
