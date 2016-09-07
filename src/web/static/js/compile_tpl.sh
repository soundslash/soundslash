#!/bin/sh
#
# npm install -g uglify-js
# npm install -g blueimp-tmpl
#
# Then run this script
#
daemon() {
    chsum1=""

    while [[ true ]]
    do
        chsum2=`find tpl/ -type f -exec md5sum {} \;`
        if [[ $chsum1 != $chsum2 ]] ; then           
            compile
            chsum1=$chsum2
        fi
        sleep 2
    done
}

compile() {
    now=$(date +"%T")
    echo -n "$now Compiling..."
    tmpl.js tpl/*.html > lib/tmpls.min.js
    echo " - OK"
}

daemon
