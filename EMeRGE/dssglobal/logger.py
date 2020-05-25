# standard libraries
import logging
import os

def getLogger(log_dict={}):

    LOG_FORMAT = "%(asctime)s:  %(levelname)s:  %(message)s"

    default_dict = {"clear_old_log_file":True,
                        "log_filename":"logs",
                        "log_folder":".",
                        "save_in_file":False}
    
    if not isinstance(log_dict,dict):
        raise TypeError(f"{log_dict} is not of type {dict} !!!")

    log_dict = {**default_dict,**log_dict}

    # Creates a log file based on setting provided on 'config.json'
    logger = logging.getLogger()
        
    if log_dict["save_in_file"]:

        # Clear old log files
        if log_dict["clear_old_log_file"]:
            log_filename = log_dict["log_filename"] + '.log'
            if  log_filename in os.listdir(log_dict["log_folder"]):
                os.remove(os.path.join(log_dict["log_folder"],log_filename))

        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, \
                        filename=os.path.join(log_dict["log_folder"],log_dict["log_filename"]))
    
    else:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

    return logger