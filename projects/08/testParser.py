import parser

psr = parser.Parser("./StackArithmetic/SimpleAdd/SimpleAdd.vm")

while(psr.hasMoreCommands()):
   psr.advance()
   if(psr.commandType()):
     print("command type is " + psr.commandType())
     if(psr.commandType() == "C_ARITHMETIC"):
       print("  " + psr.arg1())
     else:
       print("  " + psr.current_vm_cmd[0] + " " + psr.arg1() + " " + str(psr.arg2()))
   else:
     print("no command type ")
