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
