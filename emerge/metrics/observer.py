""" Module for managing metric computation subscriber and publisher. """

import abc
import time
import uuid
from typing import Dict, List
import polars

from emerge.db import db_handler

class MetricObserver(abc.ABC):
    """ Abstracte interace for metrics observers"""

    _id = str(uuid.uuid4())

    @abc.abstractmethod
    def compute(self, *args, **kwargs)-> None:
        """ All metric observer subclass must implement compute method. """

    @abc.abstractmethod
    def get_metric(self)-> Dict:
        """ All metric observer subclass must implement get_metric method. """


class MetricsSubject:
    """ Class for managing metric subscribers """

    def __init__(self):
        self.subscribers: list[MetricObserver] = []

    def _observer_exists(self, observer: MetricObserver):
        """ Check whether the observer exists or not"""
        
        for id, obs in enumerate(self.subscribers):
            if obs._id == observer._id:
                return id

        return False

    def attach(self, observer: MetricObserver):
        """ Method for attaching the observers. """
        if not self._observer_exists(observer):
            self.subscribers.append(observer)

    def detach(self, observer: MetricObserver):
        """ Method for deleting the observer object from the list. """
        
        observer_index = self._observer_exists(observer)
        if observer_index:
            self.subscribers.pop(observer_index)


    def notify(self, *args, **kwargs):
        """ Method for notifying the observers. """
        for obs in self.subscribers:
            obs.compute(*args, **kwargs)

    
def export_tinydb_json(observers: List[MetricObserver], json_path: str ):
    """ Function for exporting metrics. """
    
    db_instance = db_handler.TinyDBHandler(json_path)
    for observer in observers:
        db_instance.db.insert(
            {
                "type": "metrics", 
                "name": observer.__class__.__name__,
                "data": observer.get_metric()
            })

def export_csv(observers: List[MetricObserver], export_path):
    
    for observer in observers:
        df = polars.from_dict(observer.get_metric())
        df.write_csv(export_path / (str(observer.__class__.__name__) + '.csv'))