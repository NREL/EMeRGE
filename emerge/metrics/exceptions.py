""" Module for managing EMERGE specific exceptions. """

class BaseEmergeException(Exception):
    """ Base class for managing emerge exceptions. """

class EnergyMeterNotDefined(Exception):
    """ Exception raised because energy meter is not defined. """