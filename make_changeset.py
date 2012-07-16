#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' make_changeset.py beta

This program builds an osm diff (.osc) file for a changeset by examining minutely diffs

Copyright (c) 2012 Paul Norman

Released under the MIT license

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do 
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.

'''

import argparse
import urllib2

def retry(max_attempts, *exception_types):
    def tryIt(func):
        def f(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts-1:
                try:
                    return func(*args, **kwargs)
                except exception_types:
                    attempts += 1
            return func(*args, **kwargs)
        return f
    return tryIt

@retry(5, urllib2.URLError)
def retry_open(url):
    return urllib2.urlopen(url)

def isoToTimestamp(isotime):
    t = datetime.strptime(isotime, "%Y-%m-%dT%H:%M:%SZ")
    return time.mktime(t.timetuple())
    
if __name__ == "__main__":
    class LineArgumentParser(argparse.ArgumentParser):
        def convert_arg_line_to_args(self, arg_line):			
            if arg_line:
                if arg_line.strip()[0] == '#':
                    return	
                for arg in ('--' + arg_line).split():
                    if not arg.strip():
                        continue
                    yield arg
    parser = LineArgumentParser(description='Create a changeset .osc from replication diffs',fromfile_prefix_chars='@')
    
    parser.add_argument('changeset', type=int, help='The changeset to generate')
    
    parser.add_argument('--replication-url', help='Base URL of replication diffs', default='http://merry.paulnorman.ca:7201/minute-redaction-replicate/')
    parser.add_argument('--api-url', help='Base URL of the API', default='http://api.openstreetmap.org/')
    parser.add_argument('--retry', help='Number of times to retry a failed download', default=5)
    opts=parser.parse_args()
    print opts
    
     
    latest_state = retry_open(opts.replication_url + 'state.txt')
    state={}
    for line in latest_state:
        if line[0] == '#':
                continue
        (k, v) = line.split('=')
        state[k] = v.strip().replace("\\:", ":")
    
    print state
    changeset_xml = retry_open(opts.api_url + '/api/0.6/changeset/' + str(opts.changeset))

    print changeset_xml.read()