import re
import string
import dns
from dns import resolver
import sys


def do(args, pipe=None):
    record_type = "A"
    records = []
    print args
    print type(args)
    arg = string.split(args)
    if len(arg) == 0:
        return "No arguments given"
    elif len(arg) == 1:
        host = string.strip(string.split(args)[0])
    elif len(arg) == 2 or len(arg) == 3:
        record_type = string.strip(string.split(args)[0])
        host = string.strip(string.split(args)[1])
    elif len(arg) == 4:
        return "Usage: !dns RECORD_TYPE(default=A) www.domain.tld."

    print "----"
    print host
    print record_type
    print "----"
    if host is None:
        host = record_type
        record_type = "A"
    try:
        for record in resolver.query(host, record_type):
            print record.to_text()
            records.append(record.to_text())
        resp = records
        if record_type == "A":
            resp = re.findall(r'[0-9]+(?:\.[0-9]+){3}', str(records))
        print resp
        return str(resp)

    except:
        ex = sys.exc_info()[0]
        if ex == resolver.NoAnswer:
            return ("No Answer (" + record_type + " " + host + ")")

        if ex == resolver.NXDOMAIN:
            return("Domain not found (" + host + ")")

        if ex == resolver.NoMetaqueries:
            return ("Meta queries not allowed on (" + host + ")")

        if ex == dns.rdatatype.UnknownRdatatype:
            return ("Record type: " + record_type + " is not supported.")

        print str(ex)
        return str(ex)
