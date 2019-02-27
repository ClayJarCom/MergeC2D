# ![MergeC2D](https://github.com/ClayJarCom/MergeC2D/blob/master/MergeC2D.png) MergeC2D
Merge multiple Carbide Create .c2d files into one.

This is a simple python script to merge Carbide Create .c2d files, which are just JSON data.  This script groups the objects from each file for your convenience.

<code>MergeC2D.py main_file.c2d merge_file.c2d [more_merge_files.c2d...] -o output_merged.c2d</code>

Merging now fully supports toolpath groups.
* If the main and merge files both support or lack support for toolpath groups, nothing unusual happens.
* If the main file _does_ support toolpath groups and a merge file _does not_, the merged toolpaths will be grouped in a new group with the name of the merging file.
* If the main file _does not_ support toolpath groups a the merge file _does_, the toolpaths will be merged, but toolpath grouping is lost.
