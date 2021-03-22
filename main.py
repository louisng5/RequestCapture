import requests
from requests.adapters import HTTPAdapter
from urllib3.util import parse_url
from urllib import parse
import pickle

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
        self._captured[key] = resp
        return resp
    def dump(self,file):
        with open(file,'wb') as f:
            pickle.dump(self._captured,f)

class MockAdapter(HTTPAdapter):
    _captured = {}
    def __init__(self,filepath):
        super(MockAdapter, self).__init__()
        with open(filepath,'rb') as f:
            self.resp_dict = pickle.load(f)

    def send(self, request, stream, timeout, verify, cert, proxies,):
        return self.resp_dict[request_to_key(request)]


ss = requests.Session()
b = CaptureAdapter()
ss.mount('https://',b)
print(ss.post('https://google.com?rrr=rrr',params={'dwa':['555','6667']},json={"3":4}).text)
# b.dump('p.pickle')
