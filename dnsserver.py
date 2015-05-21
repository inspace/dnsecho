#!/usr/bin/env python
import os
import socket
import datetime
import sys
import traceback
import select
import copy
import json
from dnsrecord import *

try:
    import syslog as sl
    from syslog import openlog

    def syslog(msg):
        sl.syslog(sl.LOG_ALERT, msg)
except ImportError:
    def syslog(msg):
        sys.stderr.write('%s\n' % msg)
    def openlog(ident=None):
        pass
    

HOST = '0.0.0.0'
EMPTY = '0.0.0.0'
PORT = 53
HEXS = '0123456789abcdef'
RCLASS_IN = 1
_COLS = 16
EMPTY_LIST = []

RECORDS = {}

def add_record(name, record):
    r1 = RECORDS.get(name)
    if r1 is None:
        r1 = {}
        RECORDS[name] = r1

    rtype = record.get_record_type()
    if rtype == RTYPE_CNAME:
        # A CNAME record is not allowed to coexist with any other data.
        if 0 < len(r1.keys()) and RTYPE_CNAME not in r1:
            print 'ignore:', str(record)

    records = r1.get(rtype)
    if records is None:
        records = []
        r1[rtype] = records
    records.append(record)

def find_records(name, rtype, address):

    # Look for any records associated with this name
    records = RECORDS.get(name, EMPTY_LIST)
    if not records:
        return records
   
    # Check to see if requested rtype is in records
    record_list = []
    if rtype != QTYPE_ANY:
        record_list = records.get(rtype, record_list)       
        if not record_list and rtype != RTYPE_CNAME: #if no results
            record_list = records.get(RTYPE_CNAME, record_list)
    else:
        #return all records
        map(record_list.extend, records.values())
 
    # Return if no records, this is not an A record or if the A record is non-empty ipadrs
    if not record_list or rtype != RTYPE_A or record_list[0].ipadrs != EMPTY:
        return record_list

    """
    Now process client-specific A record requests
    """
    client_ip = address[0]

    record_list = [RecordA(1, client_ip)]

    return record_list

def def_a_record(name, ipadrs, ttl, with_ptr=True):
    add_record(name, RecordA(ttl, ipadrs))
    if with_ptr:
        rev = ipadrs.split('.')
        rev.reverse()
        rev.extend(['in-addr', 'arpa'])
        rname = '.'.join(rev)
        add_record(rname, RecordPTR(ttl, name))

def find(dname, qtype, address):

    fqdn = str(dname)
    records = find_records(fqdn, qtype, address)
    if records:
        return records
    
    dn = dname.parts[1:]
    while dn:
        nl = ['*']
        nl.extend(dn)
        nn = '.'.join(nl)
        records = find_records(nn, qtype, address)
        if records:
            return records
        
        dn.pop(0)
    
    return []

def resolve(query, address):
    try:
        res = query.create_response_template()
        found = 0 # ????????????
        for qi in query.qds:
            records = find(qi.dname, qi.qtype, address)
            #syslog('%s Query: %s Records: %s' % (address[0], str(qi), [str(x) for x in records]))

            for r in records:
                res.append_answer(qi, r)
                found += 1
        if 0 < found:
            res.close(0)
        else:
            # Name Error???
            res.close(3)
    except Exception as ex:
        res.close(2)
        print ex
    return res

def b(_bytes, n):
    iv = 0
    while 0<_bytes:
        iv <<= 8
        iv |= n()
        _bytes -= 1
    return iv

def parse_query(data):
    req = Request()
    n = data.__iter__().next

    req.id = b(2, n)
    req.flags = b(2, n)
    req.qd_count = b(2, n)
    req.an_count = b(2, n)
    req.ns_count = b(2, n)
    req.ar_count = b(2, n)

    for x in xrange(0, req.qd_count):
        q = QueryInfo()
        q.dname = DName.from_binary(n)
        q.qtype = b(2, n)
        q.qclass = b(2, n)
        req.qds.append(q)
    
    return req

def tcp_proc(ssock):
    csock, adrs = ssock.accept()
    
    recv = csock.recv(2)
    data = [ord(x) for x in recv]

    mlen = data[0]<<8 | data[1]
    recv = csock.recv(mlen)
    data = [ord(x) for x in recv]
   
    query = parse_query(data)
    res = resolve(query, adrs)

    if res is not None:
        mlen = len(res.buf)
        res.buf.insert(0, (mlen>>8) & 0xff)
        res.buf.insert(1, mlen & 0xff)
        csock.sendall(res.buf)
    
    csock.close()

def udp_proc((pstr,adrs), ssock):
    data = [ord(x) for x in pstr]
    query = parse_query(data)
    res = resolve(query, adrs)
   
    if res is not None:
        ssock.sendto(res.buf, 0, adrs)

def main():
    
    add_record('whoami.ipgeoloc.com', RecordSOA(300, 'dns1.registrar-servers.com', 'root@ipgeoloc.com', None,
                                    3600, 1800, 20000, 3600))

    #placeholders for client-specific
    add_record('whoami.ipgeoloc.com', RecordA(1, EMPTY))

    # UDP
    ssock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ssock_udp.bind((HOST, PORT))
   
    # TCP
    ssock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssock_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ssock_tcp.bind((HOST, PORT))
    ssock_tcp.listen(3)

    syslog('Server started')
    
    try:
        while 1:
            try:
                rlist, wlist, xlist = select.select([ssock_udp, ssock_tcp], [], [], 5000)
                if ssock_udp in rlist:
                    data = ssock_udp.recvfrom(1500)
                    udp_proc(data, ssock_udp)
                if ssock_tcp in rlist:
                    tcp_proc(ssock_tcp)
            except (KeyboardInterrupt, SystemExit):
                break
            except:    
                pass
    finally:
        syslog('Shutting down')
        ssock_udp.close()
        ssock_tcp.close() 
    
def b2h(v):
    return ''.join([HEXS[(v>>4)&0xf], HEXS[v&0xf]])

def dump_buffer(pack):
    i = _COLS
    for x in pack:
        i -= 1
        print b2h(x),
        if i==0:
            print
            i = _COLS
    print '<<'


if __name__=='__main__':
    openlog(ident='EchoDNSServer')
    main()
