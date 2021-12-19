import sys
import code
import parser
import symboltable

fname_asm = sys.argv[1] #should be *.asm
fname = fname_asm.split('.')[0]
fname_hack = fname + ".hack"

f_hack = open(fname_hack, "w")

psr1 = parser.Parser(fname_asm)

symTable = symboltable.SymbolTable()

while(psr1.hasMoreCommands()):
  psr1.advance()
  if(psr1.commandType() == "L_COMMAND"):
    #we reached a symbol
    #the ROM address of the current command is being tracked by Parser.hack_line
    #when we encounter a label (LBL), LBL needs to refer to the NEXT command (Parser.hack_line + 1)
    symTable.addEntry(psr1.symbol(), psr1.hack_line+1)


#second pass.  need to initialize a new parser.


psr = parser.Parser(fname_asm)

while(psr.hasMoreCommands()):
  psr.advance()
 
  #the biggest change here is that we need to handle symbols in the @ command.
  if(psr.commandType() == "A_COMMAND"):
    if(not (psr.symbol()[0]).isnumeric()): #if it is a valid symbol name
      if(symTable.contains(psr.symbol())): #first, see if it's already in symbol table.
        symbol = symTable.GetAddress(psr.symbol()) #if yes, get its meaning/address.
      else: #if not,
        #have to add the symbol to the symbol table
        symTable.addEntry(psr.symbol()) #we use the automated add.  the symbol table keeps track of available RAM address using a "pointer".
        #since used the automated add, we need to ask what the address/meaning is:
        symbol = symTable.GetAddress(psr.symbol())
      hack_code = format(symbol,'016b') + "\n"
    else: #if psr.symbol() begins with a digit (must thus be a number literal):
      #do exactly what we previously did:
      symbol = int(psr.symbol())
      hack_code = format(symbol,'016b') + "\n"     

  #C_Commands are handled exactly the same.  There are not symbols in this command.
  if(psr.commandType() == "C_COMMAND"):
    h_dest = code.dest(psr.dest() )
    h_comp = code.comp(psr.comp() )
    h_jump = code.jump(psr.jump() )

    hack_code = "111" + h_comp + h_dest + h_jump + "\n"

  if(psr.commandType() == "C_COMMAND" or psr.commandType() == "A_COMMAND"):
    f_hack.write(hack_code)

