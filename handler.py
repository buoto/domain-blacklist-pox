import json

from models import BlockedDomain
from pox.web import webcore


class BlacklistHandler(webcore.SplitRequestHandler, object):

    def __init__(self, parent, prefix, args):
        super(BlacklistHandler, self).__init__(parent, prefix, args)
        if 'blacklist' in args:
            self.blacklist = args['blacklist']


    def do_POST(self):
        data = {}
        try:
            data = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        except ValueError:
            self.respond(400, {'error': 'invalid json'})
        self.log_message(str(data))
        if 'domain' not in data:
            self.respond(400, {'error': 'missing "domain" field'})

        domain = data['domain']
        self.blacklist.add(domain)
        self.respond(201, {'domain': domain})

    def do_GET(self):
        self.respond(200, {'blacklist': [str(d) for d in self.blacklist.domains()]})

    def respond(self, status, data=None):
        self.send_response(status)
        j = json.dumps(data)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(j)))
        self.end_headers()
        if data:
            self.wfile.write(j)
