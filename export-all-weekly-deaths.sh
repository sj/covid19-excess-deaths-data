#!/bin/bash
# Collects data on weekly deaths from all available countries
set -e

tmpfile=`mktemp`
echo "country;first_day;last_day;filter;deaths;source;notes" > $tmpfile

find -type f -name "export-weekly-deaths.py" | grep NL | while read exportscript_path; do
    echo $exportscript_path
    scriptdir=`dirname "$exportscript_path"`
    scriptfile=`basename "$exportscript_path"`
    pushd "$scriptdir" # > /dev/null
    ./$scriptfile >> $tmpfile
    popd > /dev/null
done

mv "$tmpfile" "weekly-deaths.csv"
