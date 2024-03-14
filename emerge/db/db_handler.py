
"""Managing database."""

from tinydb import TinyDB

class TinyDBHandler:
    
    def __init__(self, json_path='db.json'):
        self.db = TinyDB(json_path)
