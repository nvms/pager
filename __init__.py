#!/usr/bin/env python
# -*- coding:  utf-8 -*-
from io import BytesIO

try:
    import pycurl2 as pycurl
except ImportError:
    import pycurl

import time
import re


class last_location(object):
    def __init__(self, _string):
        self._string = _string

    def __str__(self):
        return str(self._string)


class status_code(object):
    def __init__(self, _string):
        self._string = _string
        self.human = human(_string)

    def __str__(self):
        return str(self._string)

    def __unicode__(self):
        return str(self._string)


class human(status_code):
    def __init__(self, _string):
        self.human = None
        status_codes = {
            '200': 'OK',
            '202': 'Accepted',
            '204': 'No Content',
            '301': 'Moved Permanently',
            '302': 'Found',
            '307': 'Temporary Redirect',
            '308': 'Permanent Redirect',
            '400': 'Bad Request',
            '401': 'Unauthorized',
            '403': 'Forbidden'
        }
        for k, v in status_codes.items():
            if str(k) == str(_string):
                self.human = str(k + ' ' + v)

    def __str__(self):
        return str(self.human)


class Pager(object):
    def __init__(self, fqdn=False, ssl_verify=True, cookiefile_name='cookies'):

        self.content = 'NONE'
        self.status_code = None
        self.last_location = None
        self.fqdn = fqdn
        self.c = pycurl.Curl()
        self.buffer = BytesIO()

        opts = {
            self.c.WRITEFUNCTION: self.buffer.write,
            self.c.COOKIEFILE: cookiefile_name,  # file to read cookies from
            self.c.COOKIEJAR: cookiefile_name,  # file to write cookies to
            self.c.USERAGENT: 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
            self.c.SSL_VERIFYPEER: 0 if not ssl_verify else 1,
            self.c.SSL_VERIFYHOST: 0 if not ssl_verify else 2,
            self.c.FOLLOWLOCATION: 1,
            self.c.MAXREDIRS: 9
        }

        for k, v in opts.items():
            self.c.setopt(k, v)

    def juice(self, regex, num=1):
        r = re.compile(regex, re.DOTALL)
        m = r.search(self.content)
        if m:
            return m.group(num)
        else:
            return False

    def juice_all(self, regex, capture_groups={0}):
        r = re.compile(regex, re.DOTALL)
        matched = r.findall(self.content)  # matched is now a tuple
        match_list = []
        for m in matched:
            mdict = {}
            for n in capture_groups:
                mdict[n] = m[n]
            match_list.append(mdict)
        return match_list

    def has(self, match):
        if self.content.find(match) >= 0:
            return True
        else:
            return False

    def findall(self, pattern):
        return re.findall(pattern, self.content)

    def get(self, path, referer=False, dump=False, postdata=False, return_bytes=False):
        self.c.setopt(self.c.POST, 0)
        return self._request(path, referer, dump, postdata, return_bytes)

    def post(self, path, postdata=False, referer=False, dump=False, return_bytes=False):
        if postdata:  # POST is completely fine if it has no payload
            self.c.setopt(self.c.POST, 1)
            self.c.setopt(self.c.POSTFIELDS, postdata)
            # else:
            # one thing to note when passing POST request with no payload,
            # might want to pass header 'Content-Length: 0'. some proxies
            # have problems with body-less POST requests
            # self.c.setopt(self.c.HTTPHEADER, ['Content-Length: 0'])

        return self._request(path, referer, dump, postdata, return_bytes)

    def _request(self, path, referer=False, dump=False, postdata=False, return_bytes=False):
        """
        Performs the request to path.

        :param postdata: data to post
        :param return_bytes: for use with images mainly.. if path points to imagefile, can do:
            from PIL import Image; i = Image.open(io.BytesIO(<return value of _request>))
        :param path: Path to request. If self.fqdn is set when Pager() is instantiated then 'path' is appended to it
        :param referer: Used to set HTTP referer header of this request
        :param dump: If True then contents of self.content are dumped into an .html document
        :return: self.content (body of request) is returned as str
        """

        _fullpath = self.fqdn + path if self.fqdn else path

        if self.fqdn:
            self.c.setopt(self.c.URL, self.fqdn + path)
        else:
            self.c.setopt(self.c.URL, path)

        if referer:
            if self.fqdn:
                referer = self.fqdn + referer
            self.c.setopt(self.c.REFERER, referer)
        else:
            self.c.setopt(self.c.REFERER, '')

        if self.buffer.seekable():
            self.buffer.truncate(0)
            self.buffer.seek(0)

        self.c.perform()
        if not return_bytes:
            self.content = self.buffer.getvalue().decode('UTF-8')
        else:
            self.content = self.buffer.getvalue()
        self.status_code = status_code(self.c.getinfo(self.c.RESPONSE_CODE))
        if postdata:
            self.last_location = last_location(_fullpath + postdata)
        else:
            self.last_location = last_location(_fullpath)

        if dump:
            self.dump()

        return self.content

    def dump(self):
        s = str(self.last_location)
        dmp = open('dumps/' + ''.join(x for x in s if x.isalnum()) + '-' + str(int(time.time())) + '.html', 'wb')
        dmp.write(self.content.encode(encoding='utf_8'))
        dmp.close()
