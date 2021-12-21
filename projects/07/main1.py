import sys
import parser
import codewriter

arg = sys.argv[1] 
if arg.endswith(".vm"):
  #it is a file
  psr = parser.Parser(arg)
  filename_writer = arg[:-3]+".asm"
  writer = codewriter.CodeWriter(filename_writer)
  writer.setFileName(arg) #needed to set up static_namespace
  
else:
  #it is a directory
  #get all *.vm files in this directory
  #loop through them, running parser and codeWriter - note: 
  #  for each new *.vm file, we get a NEW PARSER but NOT A NEW CODEWRITER
  #    instead, call writer.setFileName(*.vm) on the codewriter for each new .vm file.
  pass #handle this case later


while(psr.hasMoreCommands()):
  psr.advance()
  if(not psr.commandType()):
    continue

  cmdType = psr.commandType()
  if(cmdType == "C_ARITHMETIC"):
    writer.writeArithmetic(psr.current_vm_cmd[0])

  elif(cmdType == "C_PUSH" or cmdType == "C_POP"):
    writer.writePushPop(psr.current_vm_cmd[0], psr.arg1(), psr.arg2()) 

  else:
    print("error: main function does not recognize command type")

writer.close()
