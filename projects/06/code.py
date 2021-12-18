# Code module
# implements the suggested API

def dest(str_dest):
  dest_mnemonic = {"null" : "000",
                   "M"    : "001",
                   "D"    : "010",
                   "MD"   : "011",
                   "A"    : "100", 
                   "AM"   : "101", 
                   "AD"   : "110", 
                   "AMD"  : "111"}
  if(str_dest in dest_mnemonic):
    return dest_mnemonic[str_dest]
  else:
    print("error in Code.dest(): dest mnemonic error from str_dest= "+str_dest)
    return

def jump(str_jump):
  jump_mnemonic = {"null" : "000",
                   "JGT"  : "001",
                   "JEQ"  : "010",
                   "JGE"  : "011",
                   "JLT"  : "100",
                   "JNE"  : "101",
                   "JLE"  : "110",
                   "JMP"  : "111"}
  if(str_jump in jump_mnemonic):
    return jump_mnemonic[str_jump]
  else:
    print("error in Code.jump(): dest mnemonic error from str_jump= "+str_jump)
    return

def comp(str_comp):
  comp_mnemonic = {"0"    : "0101010",
                   "1"    : "0111111",
                   "-1"   : "0111010",
                   "D"    : "0001100",
                   "A"    : "0110000",
                   "!D"   : "0001101",
                   "!A"   : "0110001",
                   "-D"   : "0001111",
                   "-A"   : "0110011",
                   "D+1"  : "0011111",
                   "A+1"  : "0110111",
                   "D-1"  : "0001110",
                   "A-1"  : "0110010",
                   "D+A"  : "0000010",
                   "D-A"  : "0010011",
                   "A-D"  : "0000111",
                   "D&A"  : "0000000",
                   "D|A"  : "0010101",
                   "M"    : "1110000",
                   "!M"   : "1110001",
                   "-M"   : "1110011",
                   "M+1"  : "1110111",
                   "M-1"  : "1110010",
                   "D+M"  : "1000010",
                   "D-M"  : "1010011",
                   "M-D"  : "1000111",
                   "D&M"  : "1000000",
                   "D|M"  : "1010101"}
  if(str_comp in comp_mnemonic):
    return comp_mnemonic[str_comp]
  else:
    print("error in Code.comp(): comp mnemonic error from str_comp= "+str_comp)
    return
