#!/usr/bin/env python

# quick and dirty script to parse html from the Myst Journals series body text and turn it into
# something that isn't insufferable.

import argparse
import sys
import re
import textwrap

from bs4 import BeautifulSoup

def get_cli_args():
    p = argparse.ArgumentParser(
        prog="formatmj",
        description='Script to format body text from Myst Journals copy',
    )
    
    infile_help = 'The name of the myst journals file to read. If not given, stdin will be used.'
    p.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help=infile_help)
    
    outfile_help = 'The output file to write to. If not given, stdout will be used.'
    p.add_argument('-o', '--output_file', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help=outfile_help)
    
    start_help = 'The line number of the first line of input to read from, inclusive. 1-indexed.'
    p.add_argument('-s', '--start', type=int, default=1, help=start_help)
    
    end_help = 'The line number of the last line of input to read to, inclusive. 1-indexed. A value of 0 or lower explicitly indicates to go the last line in input.'
    p.add_argument('-e', '--end', type=int, default=0, help=end_help)
    
    indent_help = 'The number of tab indents to apply to paragraph body text. Open and close <p> tags will be at this level -1, minimum 0.'
    p.add_argument('-I', '--indent', type=int, default=3, help=indent_help)
    
    tabseq_help = 'The sequence to use for a single indent. Char-length of the tab is not calculated from this but with --tab-width.'
    p.add_argument('-T', '--tab-seq', type=str, default='\t', help=tabseq_help)
    
    tablen_help = 'The character length to assume for a single indent.'
    p.add_argument('-L', '--tab-len', type=int, default=4, help=tablen_help)
    
    width_help = 'The text column for body text to wrap at.'
    p.add_argument('-W', '--width', type=int, default=100, help=width_help)
    
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
    tags = soup.body.findChildren(recursive=False)
    
    #format_p_text(args.width, args.indent, args.tab_seq, args.tab_len, tags, args.output_file)
    args.output_file.close()
    
def tag_with_attrs(t):
    
    
def format_p_text(wrap_width, level, tab_seq, tab_len, tags, outfile):
    body_tab_count = max(level, 0)
    p_tab_count = max(level-1, 0)
    body_tabs = tab_seq * body_tab_count
    p_tabs = tab_seq * p_tab_count
    
    wrapped_tab_space = max(tab_len, 1) * body_tab_count
    body_text_wrap_width = wrap_width - wrapped_tab_space
    
    for t in tags:
        if t.name == 'blockquote':
            print(t.prettify(), file=outfile)
        body_text = t.decode_contents()
        collapsed = re.sub(r'\s+', r' ', body_text.strip())
        wrapped = textwrap.wrap(collapsed, body_text_wrap_width)
        #print(p_tabs, end='', file=outfile)
        #print('<' + t.name.lower() + '>', file=outfile)
        for ln in wrapped:
            pass
            #print(body_tabs, end='', file=outfile)
            #print(ln, file=outfile)
        #print(p_tabs, end='', file=outfile)
        #print('</' + t.name.lower() + '>', file=outfile)
    outfile.flush()
    
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
