#!/usr/bin/env python

# quick and dirty script to parse html from the Myst Journals series body text and turn it into
# something that isn't insufferable.

import argparse
import sys

from bs4 import BeautifulSoup

def get_cli_args():
    p = argparse.ArgumentParser(
        prog="formatmj",
        description='Script to format body text from Myst Journals copy',
    )
    
    infile_help = 'The name of the myst journals file to read. If not given, stdin will be used.'
    p.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help=infile_help)
    
    start_help = 'The line number of the first line of input to read from, inclusive. 1-indexed.'
    p.add_argument('-s', '--start', type=int, default=1, help=start_help)
    
    end_help = 'The line number of the last line of input to read to, inclusive. 1-indexed. A value of 0 or lower explicitly indicates to go the last line in input.'
    p.add_argument('-e', '--end', type=int, default=0, help=end_help)
    
    args = p.parse_args()
    return args

def main():
    args = get_cli_args()
    f = args.input_file
    
    html_doc = ""
    lineno = 0
    for line in f:
        lineno += 1
        if lineno < args.start:
            continue
        if args.end > 0 and lineno > args.end:
            break
        html_doc += line.rstrip() + '\n'
    
    f.close()
    
    soup = BeautifulSoup(html_doc, 'html5lib')
    
    pno = 0
    for p in soup.find_all('p'):
        pno += 1
        print("P{:d}: {:s}".format(pno, p.decode_contents()))
    
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
