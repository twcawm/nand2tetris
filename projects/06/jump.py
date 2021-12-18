# Jump module
# implements the suggested API

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
    return jump_mnemonic[str_dest]
  else:
    print("error in Code.jump(): dest mnemonic error from str_jump= "+str_jump)
    return
