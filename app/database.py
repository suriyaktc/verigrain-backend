# app/database.py
class MockDB:
    def __init__(self):
        self.scans = self
    
    async def insert_one(self, data):
        if not hasattr(self, '_data'): self._data = []
        self._data.append(data)
        return True
    
    def find(self, query):
        # Returns all scans that match the status
        status = query.get("status")
        return MockCursor([d for d in getattr(self, '_data', []) if d.get("status") == status])

class MockCursor:
    def __init__(self, data):
        self.data = data
    async def to_list(self, length):
        return self.data[:length]

db = MockDB()