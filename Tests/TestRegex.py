import re

p = re.compile("\(\)")
p = re.compile('\([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?(\s*,\s*[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?){2}\)')
m = p.match("(0, 0, 0)")
if m:
    print("Match found: ", m.group())
else:
    print("No match")
