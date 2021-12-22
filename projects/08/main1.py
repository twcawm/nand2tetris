import sys
import parser
import codewriter
import glob

arg = sys.argv[1]  #this could either be a .vm file or a directory containing .vm files

if arg.endswith(".vm"):
  #it is a file
  psr = parser.Parser(arg)
  filename_writer = arg[:-3]+".asm"
  writer = codewriter.CodeWriter(filename_writer)
  writer.setFileName(arg) #needed to set up static_namespace

  while(psr.hasMoreCommands()):
    psr.advance()
    if(not psr.commandType()):
      continue

    cmdType = psr.commandType()
    if(cmdType == "C_ARITHMETIC"):
      writer.writeArithmetic(psr.current_vm_cmd[0])

    elif(cmdType == "C_PUSH" or cmdType == "C_POP"):
      writer.writePushPop(psr.current_vm_cmd[0], psr.arg1(), psr.arg2())
    elif(cmdType == "C_GOTO"):
      writer.writeGoto(psr.arg1())
    elif(cmdType == "C_IF"):
      writer.writeIf(psr.arg1())
    elif(cmdType == "C_LABEL"):
      writer.writeLabel(psr.arg1())
    elif(cmdType == "C_CALL"):
      writer.writeCall(psr.arg1(),psr.arg2())
    elif(cmdType == "C_RETURN"):
      writer.writeReturn()
    elif(cmdType == "C_FUNCTION"):
      writer.writeFunction(psr.arg1(),psr.arg2())

    else:
      print("error: main function does not recognize command type")

  writer.close()


  
else:
  #it is a directory
  #get all *.vm files in this directory
  #loop through them, running parser and codeWriter - note: 
  #  for each new *.vm file, we get a NEW PARSER but NOT A NEW CODEWRITER
  #    instead, call writer.setFileName(*.vm) on the codewriter for each new .vm file.
  if arg.endswith("/"):
    arg = arg[:-1]

  dn = arg.split("/")[-1]
  print("dn is " + dn)

  filename_writer = arg+"/"+dn+".asm"
  print("filename_writer is " + filename_writer)
  
  writer = codewriter.CodeWriter(filename_writer)

  listfiles = glob.glob(arg+"/*.vm")
  print(listfiles)

  for infile in listfiles:
    print("translating " + infile)
    writer.setFileName(infile)
    psr = parser.Parser(infile)

    #copy-pasted from single-file case:- this could be made into a function
    while(psr.hasMoreCommands()):
      psr.advance()
      if(not psr.commandType()):
        continue

      cmdType = psr.commandType()
      if(cmdType == "C_ARITHMETIC"):
        writer.writeArithmetic(psr.current_vm_cmd[0])

      elif(cmdType == "C_PUSH" or cmdType == "C_POP"):
        writer.writePushPop(psr.current_vm_cmd[0], psr.arg1(), psr.arg2())
      elif(cmdType == "C_GOTO"):
        writer.writeGoto(psr.arg1())
      elif(cmdType == "C_IF"):
        writer.writeIf(psr.arg1())
      elif(cmdType == "C_LABEL"):
        writer.writeLabel(psr.arg1())
      elif(cmdType == "C_CALL"):
        writer.writeCall(psr.arg1(),psr.arg2())
      elif(cmdType == "C_RETURN"):
        writer.writeReturn()
      elif(cmdType == "C_FUNCTION"):
        writer.writeFunction(psr.arg1(),psr.arg2())

      else:
        print("error: main function does not recognize command type")
    #note: we do NOT want to close the writer here!  we previously did this and it was a bug.
    #close the writer only after ALL files have been translated.

  writer.close()

