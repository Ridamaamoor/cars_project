# client/network_client.py
import requests
from requests.adapters import HTTPAdapter
import ssl

class HostnameIgnoreAdapter(HTTPAdapter):
    """
    Custom HTTP Adapter that forces the underlying urllib3 engine 
    to drop strict domain matching rules for self-signed certificates.
    """
    def init_poolmanager(self, *args, **kwargs):
        kwargs["assert_hostname"] = False
        return super().init_poolmanager(*args, **kwargs)

def get_secure_session(cert_path="partner.crt"):
    """
    Builds a secure requests connection session that enforces 
    cryptographic trust via a local certificate file.
    """
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(cafile=cert_path)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    
    session = requests.Session()
    adapter = HostnameIgnoreAdapter()
    adapter.poolmanager.connection_pool_kw["ssl_context"] = ssl_context
    session.mount("https://", adapter)
    return session
