import sys
import parser
import codewriter

arg = sys.argv[1] 
if arg.endswith(".vm"):
  #it is a file
  psr = parser.Parser(arg)
  writer = codewriter.CodeWriter(arg[:-3]+".asm")
  
else:
  #it is a directory
  pass #handle this case later
