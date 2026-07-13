from typing import Protocol
class SatelliteProvider(Protocol):
    def search_assets(self, *args, **kwargs): ...
    def fetch_metadata(self, *args, **kwargs): ...
    def request_processing(self, *args, **kwargs): ...
class NotConfiguredSatelliteProvider:
    status="not_configured"
    def search_assets(self,*a,**k): return {"status": self.status, "items": []}
    def fetch_metadata(self,*a,**k): return {"status": self.status}
    def request_processing(self,*a,**k): return {"status": self.status}
