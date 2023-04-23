import sys 

string = ""
for line in sys.stdin:
    string += line
print (string.replace("\n",""))