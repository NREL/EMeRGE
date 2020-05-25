""" Higher level wrapper around opendssdirect 
"""
# Standard packages
import json
import logging
import os
import datetime
import math
import time

# External packages
import opendssdirect as dss
import matplotlib.pyplot as plt
import pandas as pd

# internal modules
from dssmetrics.constants import LOG_FORMAT, DATE_FORMAT, VALID_SETTINGS, MAXITERATIONS, DEFAULT_CONFIGURATION
from dssglobal.logger import getLogger
from dssglobal.validate import validate
from dssmetrics.node_metrics import NodeMetric
from dssmetrics.line_metrics import LineMetric
from dssmetrics.transformer_metrics import TransformerMetric
from dssmetrics.customer_metric import CustomerMetric
from dssmetrics.system_metrics import SystemMetric

class OpenDSS:

    """A class for running a powerflow in a distribution feeder. This 
    class uses .json configuration file to perform a distribution 
    power flow by leveraging OpenDSS.
    """

    def __init__(self, config_data = None):

        """ Constructor for OpenDSS """

        # Default configuration 
        self.config_dict = DEFAULT_CONFIGURATION

        if config_data == None:
            json_file = open('config.json','w')
            json_file.write(json.dumps(DEFAULT_CONFIGURATION))
            json_file.close()
        else:
            # Read configuration json file
            if isinstance(config_data,str):
                with open(config_data,'r') as json_file:
                    configuartion = json.load(json_file)
                self.config_dict = {**self.config_dict,**configuartion}
            elif isinstance(config_data,dict):
                self.config_dict = {**self.config_dict,**config_data}
            else:
                raise TypeError(f"{config_data} does not match type in {[str,dict]}")

            self.validate_configuration()
            self.logger = getLogger(self.config_dict['log_settings'])

            self.dss_instance = dss

            self.logger.info("Created an OpenDSS instance.")


    def validate_configuration(self):

        # General validation
        validate(self.config_dict,VALID_SETTINGS)
                
        # Making sure important stuff exists
        if not os.path.exists(self.config_dict["dss_filepath"]):
            raise Exception(f"{self.config_dict['dss_filepath']} does not exist, simulation can not continue.")

        if not self.config_dict["dss_filename"].endswith('.dss'):
            raise Exception(f"{self.config_dict['dss_filename']} is not a vaild .dss filename")
        else:
            if self.config_dict["dss_filename"] not in os.listdir(self.config_dict["dss_filepath"]):
                raise Exception(f"{self.config_dict['dss_filename']} does not exist in {self.config_dict['dss_filepath']}")
        if not os.path.exists(self.config_dict["extra_data_path"]):
            raise Exception(f"{self.config_dict['extra_data_path']} does not exist, simulation can not continue.")
        
        if not os.path.exists(self.config_dict["export_folder"]):
            self.config_dict["export_folder"] = "."
        
        if not os.path.exists(self.config_dict["log_settings"]["log_folder"]):
            self.config_dict["log_settings"]["log_folder"] = "."

        if self.config_dict["log_settings"]["log_filename"] == "":
            self.config_dict["log_settings"]["log_filename"] = 'logs'

        if self.config_dict["record_every"] <1:
            raise ValueError(f"'record_every' can not be less than 1")

        if self.config_dict["simulation_time_step (minute)"] <=0:
            raise ValueError(f"'simulation_time_step (minute)' can not be less than equal to 0")

    def volt_var(self):

        # Setting XY curve for PV volt_var
        yarray = [str(el) for el in self.config_dict['volt_var']['yarray']]
        xarray = [str(el) for el in self.config_dict['volt_var']['xarray']]

        assert len(xarray) == len(yarray), 'length of xarray and yarray must be same !!'
        
        self.dss_instance.run_command(f"New XYCurve.vv_curve npts={len(xarray)}" \
             + " Yarray=(" + ','.join(yarray) + ") Xarray=(" + ','.join(xarray) +")")

        # Increment PVSystem
        flag = self.dss_instance.PVsystems.First()

        while flag>0:
            pv_name = self.dss_instance.PVsystems.Name()
            dss.run_command(f"New InvControl.InvPVCtrl_{pv_name} PVSystemList={pv_name} mode=VOLTVAR voltage_curvex_ref=rated "
                "vvc_curve1=vv_curve deltaQ_factor=0.08 varchangetolerance=0.00025 voltagechangetolerance=0.00001 "
                "Eventlog=No VV_RefReactivePower=VARMAX_VARS")

            flag = self.dss_instance.PVsystems.Next() 
        
    def qsts_powerflow(self):

        " Opens a opendss file and performs a powerflow."

        self.dss_instance.run_command("Clear")
        self.dss_instance.Basic.ClearAll()

        # Set the frequency for a solution (frequency always has to be set after "clear" command)
        self.dss_instance.run_command(f"Set DefaultBaseFrequency={self.config_dict['frequency']}")

        # open a opendss master fil
        success = self.dss_instance.run_command('Redirect {}'.format(os.path.join(self.config_dict["dss_filepath"], \
                                            self.config_dict["dss_filename"])))
        
        # assert that file opened successfully
        self.logger.info(success)
        assert (success==''),f"{success} - error opening file"

        
        # Set the powerflow mode to QSTS
        self.dss_instance.Solution.Mode(2)

        #set maximum control iterations
        self.dss_instance.Solution.MaxControlIterations(MAXITERATIONS)

        # Process datetime
        self.current_time = datetime.datetime.strptime(self.config_dict["start_time"],DATE_FORMAT)
        self.end_time = datetime.datetime.strptime(self.config_dict["end_time"],DATE_FORMAT)

        if self.end_time < self.current_time:
            raise Exception('End time can not be earlier !!!!')

        self.total_timesteps = int((self.end_time - self.current_time).total_seconds()/60)

        # Set start hours and seconds 
        self.dss_instance.Solution.Hour((self.current_time.timetuple().tm_yday-1)*24 
                                           + self.current_time.timetuple().tm_hour)
        
        self.dss_instance.Solution.Seconds(self.current_time.timetuple().tm_sec 
                                            + self.current_time.timetuple().tm_min*60)

        self.logger.info(f"Frequency used is : {self.dss_instance.Solution.Frequency()} Hz")

        self.logger.info(f"Simulation starting at {self.dss_instance.Solution.Hour()} hour \
                            {self.dss_instance.Solution.Seconds()} seconds")

        # set the number of solutions for each time-step to 1 
        self.dss_instance.Solution.Number(1)

        # Set the step size
        self.dss_instance.Solution.StepSizeMin(self.config_dict['simulation_time_step (minute)'])

    
        # initialize all metrics instances
        self.metric_instances = {
                                'node' :NodeMetric(self.dss_instance,self.config_dict,self.logger),
                                'line': LineMetric(self.dss_instance,self.config_dict,self.logger),
                                'trans': TransformerMetric(self.dss_instance,self.config_dict,
                                            self.logger,year=self.current_time.year),
                                'cust':CustomerMetric(self.dss_instance,self.config_dict,self.logger),
                                'system':SystemMetric(self.dss_instance,self.config_dict,self.logger)
                                }
        self.counter = 1

        while self.current_time <= self.end_time:

            # flag for storing time-series metric
            
            self.record = 0
            self.dss_instance.Solution.Number(1)
            self.dss_instance.Solution.StepSizeMin(self.config_dict['simulation_time_step (minute)'])
           
            # check if volt-var is enabled
            if self.config_dict['volt_var']['enabled']:
                self.volt_var()

            # solve the powerflow
            self.dss_instance.Solution.Solve()
           
            # log if convergence is not achieved
            if not self.dss_instance.Solution.Converged(): 
                self.logger.warning(f"Simulation NOT CONVERGED for {self.current_time}")

            # populate N_customers downward
            self.dss_instance.run_command("Relcalc")
            
            # set the flag to record
            if self.counter%self.config_dict["record_every"]==0:
                self.record = 1
                self.logger.info(f'Power flow completed for : {self.current_time}')
                
            # update the metrics
            for id,instance in self.metric_instances.items():
                if id == 'cust' or id == 'system':
                    instance.update(self.dss_instance,self.current_time,self.record,self.total_timesteps
                            ,self.metric_instances['node'],self.metric_instances['line'],self.metric_instances['trans'])
                else:
                    instance.update(self.dss_instance,self.current_time,self.record,self.total_timesteps)

            self.current_time += datetime.timedelta(minutes=self.config_dict["simulation_time_step (minute)"])
            self.counter +=1
            
        # export all the metrics
        for id, instance in self.metric_instances.items():
            instance.exportAPI(exportpath=self.config_dict['export_folder'])

    
if __name__ == '__main__':

    a = OpenDSS()
    a.qsts_powerflow()
    del a
