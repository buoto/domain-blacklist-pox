import json

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
            return
        if 'domains' not in data:
            self.respond(400, {'error': 'missing "domains" field'})
            return

        existing_domains = [d.name for d in self.blacklist.domains()]
        domains = [d for d in data['domains'] if d not in existing_domains]
        for domain in domains:
            self.log_message("Adding to blacklist: " + domain)
            self.blacklist.add(domain)
        self.respond(201, {'added': domains})

    def do_DELETE(self):
        domain = self.path.lstrip('/')
        if not domain:
            self.respond(400, {'error': 'invalid domain name'})
            return

        self.blacklist.remove(domain)

        self.respond(204)

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
