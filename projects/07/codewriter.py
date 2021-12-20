class CodeWriter:

  def __init__(self, filename):
    self.fout = open("filename", "w")
    


  def setFileName(self, filename):
    self.fin = open("filename", "w")

  def writeArithmetic(self, command):
    if("add" == command): 
      towrite = ("@SP\n" #A holds address of SP, M holds stack pointer
        "M=M-1\n" #decrement stack pointer value (this is value held at address SP)
        "A=M\n" #now, A holds address of previous top of stack 
        "D=M\n" #store value from previous top of stack
        "A=A-1\n" #point to the next-topmost address of stack (no need to update SP since we already decremented once)
        "M=M+D\n") #add D (stored previous topmost value) to M (next topmost), place it in topmost stack address
      self.fout.write(towrite)
