old_path=
new_path=
old_path_2=
new_path_2=

find  -iname "*.py" -or -iname "*.js"  -or -iname "*.html" -type f | xargs sed -i 's#pyWebMarks#exWebMarks#g'
find  -iname "*.html"  -type f | xargs sed -i 's#css/#css_ex/#g'
find  -iname "*.html"  -type f | xargs sed -i 's#js/#js_ex/#g'
