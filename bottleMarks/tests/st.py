from string import Template

all="Jim"
place="NYC"
ballhop="Tim"
a = Template('''What is $all 
the fuss about in $place 
loopers $ballhop
		''')
a = a.substitute(all=all, place=place, ballhop=ballhop)

print a
