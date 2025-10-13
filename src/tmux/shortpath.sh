#!/bin/sh
wd=$1
[ -z "$wd" ] && return

echo ${wd/#$HOME/'~'} | awk -F'/' '{
    prefix=""

    for (i = 1; i < NF; i++) {
        seg = substr($i,1,1)
        if (i == 1) {
            prefix = seg
        } else {
            prefix = prefix "/" seg
        }
    }

    print prefix "/" $NF
}' 
