#!/usr/bin/env python

# quick and dirty script to parse html from the Myst Journals series body text and turn it into
# something that isn't insufferable.

import argparse
import sys
import re
import textwrap

from typing import Tuple

import bs4

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
    
    soup = bs4.BeautifulSoup(html_doc, 'html5lib')
    nodes = soup.body.contents
    
    format_text(args.width, args.indent, args.tab_seq, args.tab_len, nodes, args.output_file)
    args.output_file.close()
    
    
def format_tag_open(t):
    tstr = '<' + t.name.lower()
    
    for at in t.attrs:
        at_val = t.attrs[at]
        if isinstance(at_val, list):
            at_val = ' '.join(at_val)
        tstr += ' ' + at + '="' + at_val + '"'
    
    #if t.isSelfClosing:
    #    tstr += '/'
    
    tstr += '>'
    return tstr
        
def format_tag_close(t):
    return '</' + t.name.lower() + '>'
    
def format_text(wrap_width, level, tab_seq, tab_len, nodes, outfile):
    body_tab_count = max(level, 0)
    tag_tab_count = max(level-1, 0)
    body_tabs = tab_seq * body_tab_count
    tag_tabs = tab_seq * tag_tab_count
    
    wrapped_tab_space = max(tab_len, 1) * body_tab_count
    body_text_wrap_width = max(wrap_width - wrapped_tab_space, 3)
    
    for elem in nodes:
        if isinstance(elem, bs4.NavigableString):
            # it is a bare string, probably it should not be so assume it should have been within
            # <p> tags.
            minisoup = bs4.BeautifulSoup('<p>' + str(elem.string) + '</p>', 'html5lib')
            elem = minisoup.body.p
        
        # from this point, elem is guaranteed to be a Tag
        tag_open = format_tag_open(elem)
            
        if elem.isSelfClosing:
            print(tag_tabs, end='', file=outfile)
            print(tag_open, file=outfile)
            continue
        
        # from this point, elem is guaranteed to be a non-self closing Tag
        tag_close = format_tag_close(elem)
        print(tag_tabs, end='', file=outfile)
        print(tag_open, file=outfile)
            
        nestables = ['blockquote', 'dl', 'div', 'center', 'small']
        if elem.name in nestables:
            # these elements can themselves contain p tags in myst journals;
            # recurse with tab level incremented.
            inner_elems = elem.contents
            format_text(wrap_width, body_tab_count+1, tab_seq, tab_len, inner_elems, outfile)
        else:
            # otherwise, assume normal text
            body_text = elem.decode_contents()
            collapsed = re.sub(r'\s+', r' ', body_text.strip())
            wrapped = textwrap.wrap(collapsed, body_text_wrap_width, break_on_hyphens=False)
            for ln in wrapped:
                print(body_tabs, end='', file=outfile)
                print(ln, file=outfile)
        
        print(tag_tabs, end='', file=outfile)
        print(tag_close, file=outfile)
    
    outfile.flush()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
