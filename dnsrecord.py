import datetime

# Record Types
RTYPE_A = 1
RTYPE_NS = 2
RTYPE_CNAME = 5
RTYPE_SOA = 6
RTYPE_PTR = 12
RTYPE_HINFO = 13
RTYPE_MX = 15
RTYPE_TXT = 16
RTYPE_AAAA = 28

QTYPE_ANY = 255

rr_map = {
    1: 'A',
    2: 'NS',
    5: 'CNAME',
    6: 'SOA',
    12:'PTR',
    13:'HINFO',
    15:'MX',
    16:'TXT',
    28:'AAAA'
}

def rtn2name(rr_value):
    return rr_map.get(rr_value, 'unknown({})'.format(rr_value))

class Record(object):
    """??????"""
    RTYPE = 0
    def __init__(self, ttl=3600):
        self._ttl = ttl
    @property
    def ttl(self):
        return self._ttl
    def to_bytes(self):
        """???????"""
        pass
    def get_record_type(self):
        return self.__class__.RTYPE
    @staticmethod
    def put16(buf, val):
        buf.append((val>>8) & 0xff)
        buf.append(val & 0xff)
    @staticmethod
    def put32(buf, val):
        buf.append((val>>24) & 0xff)
        buf.append((val>>16) & 0xff)
        buf.append((val>>8) & 0xff)
        buf.append(val & 0xff)


class RecordSOA(Record):
    """SOA??????"""
    RTYPE = RTYPE_SOA
    def __init__(self, ttl, mname, rname, serial, refresh, retry, expire, minimum):
        """???????
        mname: ?????????or?????????
        rname: ???????????
        serial: ??????
        """
        super(RecordSOA, self).__init__(ttl)
        self.mname = DName.from_name(mname)
        self.rname = DName.from_name(rname.replace('@', '.'))
        if serial:
            self.serial = serial
        else:
            # ??????????????????????
            d = datetime.datetime.utcnow()
            self.serial = ((d.year*10000 + d.month*100 + d.day) * 100 +
                                         (d.hour*4 + int(d.minute/15)))
        self.refresh = refresh
        self.retry = retry
        self.expire = expire
        self.minimum = minimum
    def to_bytes(self):
        buf = bytearray()
        self.mname.to_bytes(buf)
        self.rname.to_bytes(buf)
        self.put32(buf, self.serial)
        self.put32(buf, self.refresh)
        self.put32(buf, self.retry)
        self.put32(buf, self.expire)
        self.put32(buf, self.minimum)
        return buf
    def __str__(self):
        return 'SOA: {} {} ...'.format(str(self.mname), str(self.rname))

class RecordCNAME(Record):
    """CNAME??????"""
    RTYPE = RTYPE_CNAME
    def __init__(self, ttl, cname):
        """???????
        ttl: TTL
        cname: CNAME
        """
        super(RecordCNAME, self).__init__(ttl)
        self.cname = DName.from_name(cname)
    def to_bytes(self):
        buf = bytearray()
        self.cname.to_bytes(buf)
        return buf
    def __str__(self):
        return 'CNAME: {}'.format(str(self.cname))


class RecordA(Record):
    """A??????"""
    RTYPE = RTYPE_A
    def __init__(self, ttl, ipadrs):
        """
        ttl: TTL
        ipadrs: IP???? 'xxx.yyy.zzz.www'???
        """
        super(RecordA, self).__init__(ttl)
        self.ipadrs = ipadrs
        self.parts = [int(x) for x in ipadrs.split('.')]
    def to_bytes(self):
        buf = bytearray()
        map(buf.append, self.parts)
        return buf
    def __str__(self):
        return 'A: {}'.format(self.ipadrs)

class RecordPTR(Record):
    """PTR??????"""
    RTYPE = RTYPE_PTR
    def __init__(self, ttl, name):
        """
        ttl: TTL
        name: ????
        """
        super(RecordPTR, self).__init__(ttl)
        self.dname = DName.from_name(name)
    def to_bytes(self):
        buf = bytearray()
        self.dname.to_bytes(buf)
        return buf
    def __str__(self):
        return 'PTR: {}'.format(self.dname)

class RecordMX(Record):
    """MX??????"""
    RTYPE = RTYPE_MX
    def __init__(self, ttl, pref, name):
        """
        ttl: TTL
        pref: ???
        name: ??????????
        """
        super(RecordMX, self).__init__(ttl)
        self.pref = pref
        self.dname = DName.from_name(name)
    def to_bytes(self):
        buf = bytearray()
        buf.append((self.pref>>8) & 0xff)
        buf.append(self.pref & 0xff)
        self.dname.to_bytes(buf)
        return buf
    def __str__(self):
        return 'MX: {}: {}'.format(self.pref, self.dname)

class RecordNS(Record):
    """NS??????"""
    RTYPE = RTYPE_NS
    def __init__(self, ttl, name):
        """
        ttl: TTL
        name: ????
        """
        super(RecordNS, self).__init__(ttl)
        self.dname = DName.from_name(name)
    def to_bytes(self):
        buf = bytearray()
        self.dname.to_bytes(buf)
        return buf
    def __str__(self):
        return 'NS: {}'.format(self.dname)

class RecordTXT(Record):
    """TXT????"""
    RTYPE = RTYPE_TXT
    def __init__(self, ttl, text):
        """
        ttl: TTL
        text: ????
        """
        super(RecordTXT, self).__init__(ttl)
        self.text = text
        self.binary = text.encode('UTF-8')
    def to_bytes(self):
        buf = bytearray()
        buf.append(len(self.binary))
        map(buf.append, self.binary)
        return buf
    def __str__(self):
        return 'TXT: {}'.format(self.text)

class RecordHINFO(Record):
    """HINFO??????"""
    RTYPE = RTYPE_HINFO
    def __init__(self, ttl, cpu, os):
        """
        ttl: TTL
        cpu: CPU name
        os: OS name
        """
        super(RecordHINFO, self).__init__(ttl)
        self.b_cpu = cpu.encode('UTF-8')
        self.b_os = os.encode('UTF-8')
    def to_bytes(self):
        buf = bytearray()
        buf.append(len(self.b_cpu))
        map(buf.append, self.b_cpu)
        buf.append(len(self.b_os))
        map(buf.append, self.b_os)
        return buf
    def __str__(self):
        return 'HINFO: CPU:{} OS:{}'.format(self.b_cpu, self.b_os)


class DName:
    """domain-name class"""
    def __init__(self):
        """do not use."""
        self.parts = []
    @classmethod
    def from_name(cls, name):
        """create from string"""
        dn = DName()
        dn.parts = name.split('.')
        return dn
    @classmethod
    def from_binary(self, byte_reader):
        """create from byte sequence"""
        dn = DName()
        while 1:
            ni = byte_reader() # ?????????
            if ni==0: break # ???
            ns = []
            for xx in xrange(0, ni):
                ns.append(byte_reader())
            dn.parts.append(''.join(map(chr, ns)))
        return dn
    def __str__(self):
        return '.'.join(self.parts)
    def to_bytes(self, buf=None):
        """[??][[]][0]"""
        if buf is None:
            buf = bytearray()
        for x in self.parts:
            buf.append(len(x))
            map(buf.append, x)
        buf.append(0)
        return buf


class QueryInfo:
    """Question section"""
    def __init__(self):
        self.dname = None
        self.qtype = 0
        self.qclass = 0
    def __str__(self):
        if self.qtype==QTYPE_ANY:
            qt = 'ANY'
        else:
            qt = rtn2name(self.qtype)
        qc = {1:'RCLASS_IN'}.get(self.qclass, 'unknown: %s' % (self.qclass,))
        return '{}: {} {}'.format(str(self.dname), qt, qc)

class Request:
    def __init__(self):
        self.id = 0
        self.flags = 0
        self.qds = []
        self.nss = []
        self.ars = []
    def create_response_template(self):
        """????????????????????????"""
        res = Response()
        res.buf.append((self.id>>8) & 0xff)
        res.buf.append(self.id & 0xff)
        # ???
        flags = self.flags
        # Query/Response?1?????
        # Authoritative Answer?1????
        flags |= 0x8400
        # Recursion Available?0????
        flags &= 0xff7f
        res.put_16(flags)
        # ???????
        res.put_16(len(self.qds))
        # an/ns/ar??????0???
        for x in xrange(0, 3):
            res.put_16(0)
        # ???????
        for qi in self.qds:
            qi.dname.to_bytes(res.buf)
            res.put_16(qi.qtype)
            res.put_16(qi.qclass)
        return res


class Response:
    def __init__(self):
        self.buf = bytearray()
        self._closed = False
        self.ancount = 0 # ???
        self.nscount = 0 # ???????
        self.arcount = 0 #
    def put_16(self, b2):
        self.buf.append((b2>>8) & 0xff)
        self.buf.append(b2 & 0xff)
    def put_32(self, b4):
        self.buf.append((b4>>24) & 0xff)
        self.buf.append((b4>>16) & 0xff)
        self.buf.append((b4>>8) & 0xff)
        self.buf.append(b4 & 0xff)
    def append_answer(self, qinfo, record):
        # TODO: ??
        self.buf.extend(qinfo.dname.to_bytes())
        # ANY??A????????????????????????
        self.put_16(record.get_record_type())
        self.put_16(qinfo.qclass)
        self.put_32(record.ttl)
        rdata = record.to_bytes()
        self.put_16(len(rdata))
        map(self.buf.append, rdata)
        self.ancount += 1
    def close(self, rcode):
        """????????????????????
        rcode: ????????return code
        """
        if self._closed: return
        self._closed = True
        # return code
        self.buf[3] |= rcode & 0x0f
        # ???????
        self.buf[6] = (self.ancount>>8) & 0xff
        self.buf[7] = self.ancount & 0xff

