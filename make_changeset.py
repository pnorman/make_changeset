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
import xml.etree.cElementTree as ElementTree
from datetime import datetime
import time
import math
import gzip
import StringIO
import sys

opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'make_changeset/0.0.1')]
urllib2.install_opener(opener)

''' Some support functions '''
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
    t = datetime.strptime(isotime, '%Y-%m-%dT%H:%M:%SZ')
    return time.mktime(t.timetuple())
    
def print_cs_info(cs):
    print 'Found changeset ' + cs.get('id') + ' by ' + cs.get('user') + ' (' + cs.get('uid') + ')'
    print 'Changeset spans ' + cs.get('created_at') + ' to ' + cs.get('closed_at')


def sequence_before_date(target, startsequence, period):
    sequence = startsequence
    currentdate = date_from_sequence(sequence)
    while currentdate > target:
        sequence -= int(math.ceil(float(currentdate-target)/period))
        currentdate = date_from_sequence(sequence)
    return int(sequence)

def sequence_after_date(target, startsequence, period):
    sequence = startsequence
    currentdate = date_from_sequence(sequence)
    while currentdate < target:
        sequence += int(math.ceil(float(target-currentdate)/period))
        currentdate = date_from_sequence(sequence)
    return int(sequence)
    

def date_from_sequence(sequence):
    sqnStr = str(int(sequence)).zfill(9)
    statefile = retry_open(opts.replication_url + '%s/%s/%s.state.txt' % (sqnStr[0:3], sqnStr[3:6], sqnStr[6:9]))

    for line in statefile:
        if line[0] == '#':
                continue
        (k, v) = line.split('=')
        if k == 'timestamp':
            return isoToTimestamp(v.strip().replace("\\:", ":"))
    
if __name__ == "__main__":
    replicate_period = {'minute': 60.0,
                        'hour': 60.0*60.0}
                        #'day': 60.0*60.0*24.0} day doesn't appear to work?
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
    
    parser.add_argument('--replicate-period', choices=replicate_period.keys(), help='Force using minute, hour, or day replication diffs (default: autodetect from replicate URL, else minute)')
    parser.add_argument('--replication-url', help='Base URL of replication diffs', default='http://planet.osm.org/redaction-period/minute-replicate/')
    parser.add_argument('--api-url', help='Base URL of the API', default='http://api.openstreetmap.org/')
    parser.add_argument('--retry', help='Number of times to retry a failed download', default=5)
    opts=parser.parse_args()

    # replicate period was manually set
    if opts.replicate_period:
        opts.replicate_period = replicate_period[opts.replicate_period]
    # auto-detect replicate period
    else:
        for period in replicate_period.keys():
            if period in opts.replication_url:
                opts.replicate_period = replicate_period[period]

    # replicate period not set, and couldn't auto-detect… full back to minutes
    if not opts.replicate_period:
        opts.replicate_period = replicate_period['minute']


    print opts
    
    for line in retry_open(opts.replication_url + 'state.txt'):
        if line[0] == '#':
            continue
        (k, v) = line.split('=')
        if k == 'sequenceNumber':
            latest_sequence = int(v.strip())
    
    changeset_xml = retry_open(opts.api_url + '/api/0.6/changeset/' + str(opts.changeset))

    changeset_tree = ElementTree.parse(changeset_xml)
    for cs in changeset_tree.getroot().findall("changeset"):
        if str(opts.changeset) == cs.get('id'):
            break
            
    print_cs_info(cs)
    
    start_sequence = sequence_before_date(isoToTimestamp(cs.get('created_at')),latest_sequence, opts.replicate_period)
    end_sequence = sequence_after_date(isoToTimestamp(cs.get('closed_at')),start_sequence, opts.replicate_period)
    
    output_root = ElementTree.Element('osmChange')
    output_root.set('version','0.6')
    output_root.set('generator','make_changeset')
    action_element = None

    print 'Sequence range is %d to %d' % (start_sequence, end_sequence)
    for sequence in range(start_sequence,end_sequence):
        print 'Parsing %s' %sequence
        
        sqnStr = str(int(sequence)).zfill(9)
        
        diff_xml = gzip.GzipFile(fileobj=StringIO.StringIO(retry_open(opts.replication_url + '%s/%s/%s.osc.gz' % (sqnStr[0:3], sqnStr[3:6], sqnStr[6:9])).read()))
        diff_tree = ElementTree.parse(diff_xml)
        
        for action in diff_tree.getroot():
            for object in action:
                if opts.changeset == int(object.get('changeset')):
                    if action_element == None or action_element.tag != action.tag:
                        action_element = ElementTree.Element(action.tag)
                        action_element.tail='\n'
                        output_root.append(action_element)
                    action_element.append(object)
                
        diff_tree.getroot().clear()        
    output_tree = ElementTree.ElementTree(output_root)
    output_tree.write(str(opts.changeset)+'.osc',encoding="UTF-8")

