#!/usr/bin/bash

c_to_prod()
{
	for i in `ls *.prd`
	do
	   echo $i
	   echo ${i/.prd/}
	   ln -sf $i  ${i/.prd/}
	done
}

c_to_dev()
{
	for i in `ls *.dev`
	do
	   echo $i
	   echo ${i/.dev/}
	   ln -sf $i  ${i/.dev/}
	done
}


usage()
{

    echo -e "convert -p convert to production  \n" \
         "convert -d convert to development  \n"  \
         "usage   \n"  
}
        	


while getopts ":pd" opt; do
    case $opt in
      p) c_to_prod ;;
      d) c_to_dev ;;
      u) usage ;;
     \?) usage ;;
    esac
done



