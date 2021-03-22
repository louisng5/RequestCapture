import requests
from requests.adapters import HTTPAdapter
from urllib3.util import parse_url
from urllib import parse
import pickle
requests.sessions

def request_to_key(request):
    ps = parse_url(request.url)
    qs = parse.parse_qs(ps.query)
    key = (request.method, request.body, ps.scheme, ps.auth, ps.host, ps.port, ps.path, ps.fragment,
           str(sorted(i for i in qs.items())))
    return key

class CaptureAdapter(HTTPAdapter):
    _captured = {}
    def send(self, request, stream, timeout, verify, cert, proxies,):
        key = request_to_key(request)
        resp =  super(CaptureAdapter, self).send(request, stream, timeout, verify, cert, proxies)
        self.__class__._captured[key] = resp
        return resp

    @classmethod
    def dump(cls,file):
        with open(file,'wb') as f:
            pickle.dump(cls._captured,f)

class MockAdapter(HTTPAdapter):
    _captured = {}
    def __init__(self,filepath):
        super(MockAdapter, self).__init__()
        with open(filepath,'rb') as f:
            self.resp_dict = pickle.load(f)

    def send(self, request, stream, timeout, verify, cert, proxies,):
        return self.resp_dict[request_to_key(request)]

class AdapterContext():
    _adapter = None
    def __init__(self,filepath):
        self.filepath = filepath
        self.origional_init = requests.Session.__init__

    def __enter__(self):
        def __init__(request_self, *args, **kwargs):
            self.origional_init(request_self, *args, **kwargs)
            request_self.mount('https://', self._adapter())
            request_self.mount('http://', self._adapter())
        setattr(requests.Session, '__init__', __init__)

    def __exit__(self, exc_type, exc_val, exc_tb):
        setattr(requests.Session, '__init__', self.origional_init)


class RequestCaptureContext(AdapterContext):
    _adapter = CaptureAdapter
    def __exit__(self, exc_type, exc_val, exc_tb):
        super(RequestCaptureContext, self).__exit__(exc_type, exc_val, exc_tb)
        CaptureAdapter.dump(self.filepath)
        
class MockContext(AdapterContext):
    _adapter = MockAdapter

