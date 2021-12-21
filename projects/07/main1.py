import sys
import parser
import codewriter

arg = sys.argv[1] 
if arg.endswith(".vm"):
  #it is a file
  psr = parser.Parser(arg)
  filename_writer = arg[:-3]+".asm"
  writer = codewriter.CodeWriter(filename_writer)
  
else:
  #it is a directory
  pass #handle this case later


while(psr.hasMoreCommands()):
  psr.advance()
  if(not psr.commandType()):
    continue

  cmdType = psr.commandType()
  if(cmdType == "C_ARITHMETIC"):
    writer.writeArithmetic(psr.current_vm_cmd[0])

  if(cmdType == "C_PUSH"):
    writer.writePushPop(psr.current_vm_cmd[0], psr.arg1(), psr.arg2()) 

writer.close()
