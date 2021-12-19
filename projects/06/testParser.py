#some tests for parser
import parser
psr = parser.Parser("max/MaxL.asm")

while(psr.hasMoreCommands()):
  psr.advance()
  if(psr.commandType() == "A_COMMAND"):
    print(psr.commandType() + " ||| symbol: " + psr.symbol() )
  if(psr.commandType() == "C_COMMAND"):
    print(psr.commandType() + " ||| dest: " + psr.dest() + " ||| comp: " + psr.comp()+ " ||| jump: " + psr.jump() )
  if(psr.commandType() == "L_COMMAND"):
    print(psr.commandType() + " ||| symbol: " + psr.symbol() )
  if(psr.commandType() == None):
    print("no command.")
  print("asm_line: "+str(psr.asm_line)+ " hack_line: "+str(psr.hack_line))
