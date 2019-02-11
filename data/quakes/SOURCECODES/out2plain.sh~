#!/bin/bash
ini=$(grep -n "77777777" $1 |cut -f 1 -d':')
end=$(grep -n "99999999" $1 |cut -f 1 -d':')
size=$((end-ini-1))
#head -n $((end-1)) $1 |tail -n $size |sed -e "s/\*\*\*\*\*\*\*\*\*\*/ 0.0/"
head -n $((end-1)) $1 |tail -n $size 
