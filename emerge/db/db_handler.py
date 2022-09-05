
"""
Managing database
"""

# third-party imports
from tinydb import TinyDB, Query

class TinyDBHandler:
    
    def __init__(self, json_path='db.json'):
        self.db = TinyDB(json_path)
