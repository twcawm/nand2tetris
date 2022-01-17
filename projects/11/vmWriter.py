class VMWriter:
  def __init__(self, fout):
    self.fout = fout #assume the driver (jackCompiler) already opened the file

  def writePush(self, segment, index): #already handled by VM
    self.fout.write("push " + segment + " " + str(index) + "\n")

  def writePop(self, segment, index): #already handled by VM
    self.fout.write("pop " + segment + " " + str(index) + "\n")

  def writeArithmetic(self, command): #very simple: just the command itself
    self.fout.write(command + "\n")

  def writeLabel(self, label):
    self.fout.write("label " + label + "\n")

  def writeGoto(self, label):
    self.fout.write("goto " + label + "\n")

  def writeIf(self, label): #VM implementation handles indexing for if/goto flow control
    self.fout.write("if-goto " + label + "\n")

  def writeCall(self, name, nArgs):
    self.fout.write("call " + name + " " + str(nArgs) + "\n")
  
  def writeFunction(self, name, nLocals):
    self.fout.write("function " + name + " " + str(nLocals) + "\n")

  def writeReturn(self):
    self.fout.write("return\n")
