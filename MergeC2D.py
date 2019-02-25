#/usr/bin/env python3
"""
Merge any number of Carbide Create .c3d files into a single merged .c2d file.

This script was written by Nathaniel Klumb
and is hereby dedicated to the public domain.
"""
import json
from uuid import uuid4
from argparse import ArgumentParser,FileType

def load_c2d(c2d_file):
    """ Load a Carbide Create .c2d file, grouping all its objects. """
    c2d = json.load(c2d_file)
    # Generate a {UUID} so we can group all the objects in the file.
    group = '{{{}}}'.format(uuid4())
    for block in c2d:
        for item in c2d[block]:
            try:
                # Where we find a 'group_id' list, add our new group.
                # In Carbide Create, the first group_id is the most
                # deeply nested grouping, so we simply append ours.
                item['group_id'] += [group]
            except (TypeError, KeyError):
                pass
    return c2d

def merge_c2d(main_c2d, merge_c2d):
    """ Merge the data from a new .c2d file into data from a main file. """
    for key in merge_c2d:
        # "DOCUMENT_VALUES" is the Job Setup data.
        # The Job Setup data in merged files is ignored.
        if (key != 'DOCUMENT_VALUES'):
            if (key in main_c2d):
                main_c2d[key] += merge_c2d[key]
            else:
                main_c2d[key] = merge_c2d[key]
    return main_c2d

def save_c2d(c2d, c2d_file):
    """ Save a .c2d file for Carbide Create. """
    json.dump(c2d, c2d_file, indent=4, sort_keys=True)

if __name__ == '__main__':
    parser = ArgumentParser(
        description='Merge multiple Carbide Create .c2d files into one.'
    )
    parser.add_argument('main_file',
                        type=FileType('rU'),
                        help='Main file: Job Setup preserved.')
    parser.add_argument('merge_file',nargs='+',
                        type=FileType('rU'),
                        help='Merge objects/toolpaths from each merge_file.')
    parser.add_argument('-o','--output',
                        type=FileType('w'),
                        help='Filename to save merged .c2d')
    args = parser.parse_args()

    c2d = load_c2d(args.main_file)
    for merge in args.merge_file:
      c2d = merge_c2d(c2d, load_c2d(merge))
    save_c2d(c2d, args.output)
