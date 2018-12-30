import argparse
import httplib
import errno
from socket import error as socket_error
import json

server_addr = 'localhost:8000'
conn_refused_error_msg = "Error: Server currently not available. Make sure you started POX controller."

PATH = '/blacklist'

def handle_add_domains(domains):
    try:
        conn = httplib.HTTPConnection(server_addr)
        conn.request("POST", PATH, json.dumps({'domains': domains}))
        resp = conn.getresponse()
        raw_resp = resp.read()
        print raw_resp
    except socket_error as serr:
        if serr.errno == errno.ECONNREFUSED:
            print conn_refused_error_msg
            exit()
        raise


def handle_remove_domains(domains_to_remove):
    try:
        conn = httplib.HTTPConnection(server_addr)
        for domain in domains_to_remove:
            conn.request("DELETE", "{}/{}".format(PATH, domain))
            resp = conn.getresponse()
            raw_resp = resp.read()
            print raw_resp
    except socket_error as serr:
        if serr.errno == errno.ECONNREFUSED:
            print conn_refused_error_msg
            exit()
        raise


def handle_list_domains():
    try:
        conn = httplib.HTTPConnection(server_addr)
        conn.request("GET", PATH)
        resp = conn.getresponse()
        data = json.loads(resp.read())
        domains = data['blacklist']
        if len(domains) == 0:
            print "No blacklisted domains."
        else:
            print "Blacklisted domains:"
            for i, d in enumerate(domains):
                print str(i + 1) + ": " + d
    except socket_error as serr:
        if serr.errno == errno.ECONNREFUSED:
            print conn_refused_error_msg
            exit()
        raise

def get_parser():
    parser = argparse.ArgumentParser(description='Cli helps managing blacklisted domains in the network.')

    parser.add_argument('action', metavar='action', type=lambda x: x, nargs=1,
                        help="'add' | 'remove' | 'list'")
    parser.add_argument('domain', metavar='domain', type=lambda x: x, nargs='*',
                        help="domains to be added/removed (ignored when given action = 'list')")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.action[0] == 'add' or args.action[0] == 'remove':
        if len(args.domain) == 0:
            parser.print_help()
            print "\nError: domain name(s) not specified"
            exit()

    if args.action[0] == 'add':
        handle_add_domains(args.domain)
    elif args.action[0] == 'remove':
        handle_remove_domains(args.domain)
    elif args.action[0] == 'list':
        handle_list_domains()
    else:
        parser.print_help()
        print("\nError: cannot understand action: " + args.action[0])
        exit()

if __name__ == "__main__":
    main()




