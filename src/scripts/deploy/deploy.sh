#!/bin/bash

source "./deploy-dev.config"

echo -n "Enter pass for GIT: "
read git_pass

output_dir="output/"`date +"%Y-%m-%d_%H-%M-%S"`
mkdir -p $output_dir

function deploy {
  group_i=$1
  cat $2 | while read host; do
    output=${output_dir}/${group_i}-${host}.log
    touch $output

    printf "\n\n==========\nDeploy of $3 to $host\n==========\n\n" >> $output
    IFS='@' read -a array <<< "$host"
    IFS=':' read -a array2 <<< "${array[0]}"

    usr=${array2[0]}
    pass=${array2[1]}
    hst=${array[1]}

    expect execute.expect ${usr} ${pass} ${hst} $3 ${output} ${git_pass}
  done
}

i=1
next="group$i[lst]"
while [ ! -z ${!next} ]; do

  group="group$i"
  list="$group[lst]"
  cmds="$group[cmds]"

  deploy $group ${!list} ${!cmds}
  ((i++))
  next="group$i[lst]"
done
