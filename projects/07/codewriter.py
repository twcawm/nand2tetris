class CodeWriter:

  def __init__(self, filename):
    self.fout = open(filename, "w")
    self.labelCount = 0


  def newLabel(self):
    self.labelCount = self.labelCount + 1
    return "LABEL"+str(self.labelCount).zfill(3)
    


  def setFileName(self, filename):
    self.fin = open(filename, "w")

  def writeArithmetic(self, command):
    if("add" == command): 
      towrite = ("@SP\n" #A holds address of SP, M holds stack pointer
        "M=M-1\n" #decrement stack pointer value (this is value held at address SP)
        "A=M\n" #now, A holds address of previous top of stack 
        "D=M\n" #store value from previous top of stack
        "A=A-1\n" #point to the next-topmost address of stack (no need to update SP since we already decremented once)
        "M=M+D\n") #add D (stored previous topmost value) to M (next topmost), place it in topmost stack address

    elif("sub" == command): #sub should be almost the same as add, but must negate y (the first item popped)
      towrite = ("@SP\n" #A holds address of SP, M holds stack pointer
        "M=M-1\n" #decrement stack pointer value (this is value held at address SP)
        "A=M\n" #now, A holds address of previous top of stack
        "D=-M\n" #store value from previous top of stack.  negate it here; we'll use addition later
        "A=A-1\n" #point to the next-topmost address of stack (no need to update SP since we already decremented once)
        "M=M+D\n") #add D (stored previous topmost value) to M (next topmost), place it in topmost stack address

    elif("neg" == command):
      towrite = ("@SP\n"
        "A=M-1\n" #A holds address of topmost stack value
        "M=-M\n" #negate value at top of stack (note: this shortcut bypasses popping/pushing etc.  but it should work)
        )

    elif("eq" == command): #x == y (y top of stack, x 1 below)
      eq_label = newLabel()
      towrite = ("@SP\n"
        "M=M-1\n" #decrement value of stack pointer
        "A=M\n" #point to top of stack (y)
        "D=M\n" #store that value in D (y)
        "@SP\n"
        "M=M-1\n" #decrement value of stack pointer again
        "A=M\n" #point to next value in stack (x) (now y is in D and x is in M)
        "D=M-D\n" #THIS IS x - y. store the difference of the top 2 stack values in D (x-y)
        #we want x - y because if (x-y > 0), x > y, elif (x-y < 0), x < y.  this is the order we want.
        "M=-1\n" #-1 means true (x == y) : we put this on the stack. note stack ptr is now 1 off (too small)

        "@"+eq_label+"\n" 
        "D;JEQ\n" #if D is 0 (x==y), we are done : go to end label

        "@SP\n" #else, get the top of stack back in register and set that value to false
        "A=M\n"
        "M=0\n" #0 means false here

        "("+eq_label+")\n" #end: have to increment stack pointer (we decremented twice, have to increment once)
        "@SP\n"
        "M=M+1\n"
        )

    #note: eq, lt, gt have identical form other than which jump (JEQ, JLT, JGT) to use.
    #      so a possible future improvement could be to modularize this and only in sert the correct jump command.
    #      for now we will just keep the full form since it only repeats twice.
    elif("gt" == command): #x > y (y top of stack, x 1 below)
      eq_label = newLabel()
      towrite = ("@SP\n"
        "M=M-1\n" #decrement value of stack pointer
        "A=M\n" #point to top of stack (y)
        "D=M\n" #store that value in D (y)
        "@SP\n"
        "M=M-1\n" #decrement value of stack pointer again
        "A=M\n" #point to next value in stack (x) (now y is in D and x is in M)
        "D=M-D\n" #D=(x-y)
        "M=-1\n" #-1 means true

        "@"+eq_label+"\n"
        "D;JGT\n" #if D greater than 0 (x > y), we are done : go to end label

        "@SP\n" #else, get the top of stack back in register and set that value to false
        "A=M\n"
        "M=0\n" #0 means false here

        "("+eq_label+")\n" #end: have to increment stack pointer (we decremented twice, have to increment once)
        "@SP\n"
        "M=M+1\n"
        )
        
    elif("lt" == command): #x < y (y top of stack , x 1 below)
      eq_label = newLabel()
      towrite = ("@SP\n"
        "M=M-1\n" #decrement value of stack pointer
        "A=M\n" #point to top of stack (y)
        "D=M\n" #store that value in D (y)
        "@SP\n"
        "M=M-1\n" #decrement value of stack pointer again
        "A=M\n" #point to next value in stack (x) (now y is in D and x is in M)
        "D=M-D\n" #D=(x-y)
        "M=-1\n" #-1 means true

        "@"+eq_label+"\n"
        "D;JLT\n" #if D is less than 0 (x < y), we are done : go to end label

        "@SP\n" #else, get the top of stack back in register and set that value to false
        "A=M\n"
        "M=0\n" #0 means false here

        "("+eq_label+")\n" #end: have to increment stack pointer (we decremented twice, have to increment once)
        "@SP\n"
        "M=M+1\n"
        )

    elif("and" == command): #x and y, bitwise
      towrite = ("@SP\n" #A holds address of SP, M holds stack pointer
        "M=M-1\n" #decrement stack pointer value (this is value held at address SP)
        "A=M\n" #now, A holds address of previous top of stack
        "D=M\n" #store value from previous top of stack
        "A=A-1\n" #point to the next-topmost address of stack (no need to update SP since we already decremented once)
        "M=M&D\n") # note: this command is idential to ADD except for this: we M|D instead of M+D.

    elif("or" == command): #x or y, bitwise
      towrite = ("@SP\n" #A holds address of SP, M holds stack pointer
        "M=M-1\n" #decrement stack pointer value (this is value held at address SP)
        "A=M\n" #now, A holds address of previous top of stack
        "D=M\n" #store value from previous top of stack
        "A=A-1\n" #point to the next-topmost address of stack (no need to update SP since we already decremented once)
        "M=M|D\n") # note: this command is idential to ADD except for this: we M|D instead of M+D.
  
    elif("not" == command): #not y, bitwise.  this is almost identical to negative y
      towrite = ("@SP\n"
        "A=M-1\n" #A holds address of topmost stack value
        "M=!M\n") #negate value at top of stack (note: this shortcut bypasses popping/pushing etc.  but it should work)
  
    else:
      print("error in writeArithmetic, command " + command + " not recognized")

    self.fout.write(towrite) #write the constructed assembly to file.


  def writePushPop(self, command, segment, index): #self, string, string, int
    if("push" == command):
      if("constant" == segment):
        towrite = ("@"+str(index)+"\n" #place constant into A
          "D=A\n" #store the constant in D
          "@SP\n" #put stack pointer in M
          "A=M\n" #load stack pointer into A (now M refers to value 1 past top of stack)
                  #is there a way to do this with @M?  Not sure if @M does the same thing.  this is probably more clear
          "M=D\n" #store constant at new top of stack
          "@SP\n" #get ready to increment stack pointer
          "M=M+1\n") #increment stack pointer
          
      else:
        pass #other forms of Push implemented later
    else:
      pass #Pop etc. implemented later

    self.fout.write(towrite) #write the constructed assembly to file.

  def close(self):
    self.fout.close()
