#/usr/bin/env python3
"""
Merge any number of Carbide Create .c3d files into a single merged .c2d file.

MIT License

Copyright (c) 2019 Nathaniel Klumb

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import json
from os.path import basename,splitext
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

def merge_c2d(main_c2d, merge_c2d, group_name):
    """ Merge the data from a new .c2d file into data from a main file. """
    for key in merge_c2d:
        # For toolpath group objects and toolpath objects, we either treat
        # them normally if both files have matching capabilities, or we
        # group/ungroup the toolpath objects as necessary to merge into the
        # main file.  New groups get the merging file's name.        
        if (key = 'TOOLPATH_GROUP_OBJECTS'):
            if 'TOOLPATH_GROUP_OBJECTS' in main_c2d:
                main_c2d[key] += merge_c2d[key]
            else:
                # The main file doesn't have toolpath groups,
                # so merge each set of grouped toolpaths.
                for group in merge_c2d[key]:
                    if ('TOOLPATH_OBJECTS' in main_c2d):
                        main_c2d['TOOLPATH_OBJECTS'] +=
                            group['TOOLPATH_OBJECTS']
                    else:
                        main_c2d['TOOLPATH_OBJECTS'] =
                            group['TOOLPATH_OBJECTS']
        elif (key = 'TOOLPATH_OBJECTS'):
            if 'TOOLPATH_GROUP_OBJECTS' in main_c2d:
                # The main file does have toolpath groups,
                # so add the toolpaths as a new group.
                main_c2d['TOOLPATH_GROUP_OBJECTS'] += {
                    'TOOLPATH_OBJECTS': merge_c2d[key],
                    'enabled': True,
                    'name': group_name,
                    'uuid': '{{{}}}'.format(uuid4())
                }
            else:
                if (key in main_c2d):
                    main_c2d[key] += merge_c2d[key]
                else:
                    main_c2d[key] = merge_c2d[key]
                    
        # "DOCUMENT_VALUES" is the Job Setup data.
        # The Job Setup data in merged files is ignored.\
        elif (key != 'DOCUMENT_VALUES'):
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
      c2d = merge_c2d(c2d, load_c2d(merge), splitext(basename(merge.name))[0])
    save_c2d(c2d, args.output)
