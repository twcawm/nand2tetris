import sys
import code
import parser

fname_asm = sys.argv[1] #should be *.asm
fname = fname_asm.split('.')[0]
fname_hack = fname + ".hack"

f_hack = open(fname_hack, "w")

psr = parser.Parser(fname_asm)


#implement non-symbol assembler:
while(psr.hasMoreCommands()):
  psr.advance()
  
  if(psr.commandType() == "A_COMMAND"):
    symbol = int(psr.symbol()) #for now this will work - when we handle true symbols, we'll need to update this
    hack_code = format(symbol,'016b') + "\n" 

  if(psr.commandType() == "C_COMMAND"):
    h_dest = code.dest(psr.dest() )
    h_comp = code.comp(psr.comp() )
    h_jump = code.jump(psr.jump() )

    hack_code = "111" + h_comp + h_dest + h_jump + "\n"

  if(psr.commandType() == "C_COMMAND" or psr.commandType() == "A_COMMAND"):
    f_hack.write(hack_code)
