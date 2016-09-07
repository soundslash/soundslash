cat $1|tr '\n' ' '|awk '{v=0;for(i=0;i<NF;i++) v=v+$i;; print v/NF }'
