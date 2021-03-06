#there are a few ways we could do this.  probably it is best to implement as a class since we have a state (user-defined symbols) to encapsulate.
#note: even though we have both label and variable symbols,
#  symbolTable only  needs to track variable symbols
#  because label symbols are taken care of via the ROM tracker
#  which is basically already mostly implemented in the parser.

class SymbolTable:
  predefined_symbols = {
      "SP"   : 0,
      "LCL" : 1, 
      "ARG" : 2,
      "THIS": 3,
      "THAT": 4,
      "R0"  : 0,
      "R1"  : 1,
      "R2"  : 2,
      "R3"  : 3,
      "R4"  : 4,
      "R5"  : 5,
      "R6"  : 6,
      "R7"  : 7,
      "R8"  : 8,
      "R9"  : 9,
      "R10"  : 10,
      "R11"  : 11,
      "R12"  : 12,
      "R13"  : 13,
      "R14"  : 14,
      "R15"  : 15,
      "SCREEN": 16384,
      "KBD"  : 24576
    }
  def __init__(self):
    self.table = self.predefined_symbols  
    self.ram_pointer = 16 #we use ram_pointer to point to next available RAM for allocation
    #is this even necessary?  we might never use it.
    #with the default implementation, it is not necessary.  but it would be useful
    #  to make "address" in addEntry an optional argument, so that SymbolTable itself can automatically
    #  add entries without needing an address manually passed in.

  def addEntry(self, symbol, address=None):
    #print("adding entry " + symbol)
    if(symbol in self.table):
      print("error in symboltable: trying to add symbol that is already bound")
    else:
      if(address):
        self.table[symbol] = address #just assign into dictionary
        #ordinarily we would probably want to do more error checking, but this should do.
      else:
        #first, check if current ram_pointer is taken.  if so, increment it and retry
        '''
        if (False): #self.ram_pointer in self.table.values(): #if ram_pointer is already taken, do not overwrite
          #note: we don't want to check this because both ROM and RAM addresses can be used in the table.
          self.ram_pointer = self.ram_pointer + 1
          self.addEntry(symbol) #this is a recursive call to try again with a new ram_pointer.  not very elegant.  but if we only use the no-address version , this should never happen.
        '''
        #update: we do not want to do error checking here since the single symbol table is used for both ROM and RAM addresses (which need not be distinct)
        # a better implementation might try to use 2 symbol tables or some other flag, but this should do for now.
        self.table[symbol] = self.ram_pointer
        self.ram_pointer = self.ram_pointer + 1 

  def contains(self, symbol):
    return (symbol in self.table)

  def GetAddress(self, symbol):
    if(symbol in self.table):
      return self.table[symbol]
    else:
      print("error in symboltable: trying to GetAddress of symbol that is not bound")
