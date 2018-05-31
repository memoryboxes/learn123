#!/bin/bash
#./sort_uniq.sh file_to_be_sort file_sorted 5000M

#lines=$(wc -l $1 | sed 's/ .*//g')
#lines_per_file=`expr $lines / 100`
#split -d -l $lines_per_file $1 __part_$1
split -d -b $3 $1 __part_split

for file in __part_*
do
{
  sort -uo sort_$file $file
  rm -rf $file
} &
done
wait

sort -smu sort_* > $2
rm -f __part_*
rm -f sort_*
