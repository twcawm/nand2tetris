class CodeWriter:

  def __init__(self, filename): #this filename is of the form *.asm (something[:-4])
    self.fout = open(filename, "w")
    self.labelCount = 0


  def newLabel(self):
    self.labelCount = self.labelCount + 1
    return "LABEL"+str(self.labelCount).zfill(3)
    


  def setFileName(self, filename): #this filename is of the form *.vm (something[:-3])
    self.fin = open(filename, "w")
    if(filename.endswith(".vm")):
      self.static_namespace = filename[:-3]
      self.static_namespace = self.static_namespace.split('/')[-1] #we don't want full path, just final name
    else:
      print("error in setFileName: does not end with '.vm'")

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
      eq_label = self.newLabel()
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
      eq_label = self.newLabel()
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
      eq_label = self.newLabel()
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
          
      #note: LCL and ARG are extremely similar, only differ by using @LCL vs @ARG
      #  update: THIS and THAT are also exactly the same.
      # could improve this in the future by modularizing to share all commands except that.  but then again it only repeats once.
      #note: TEMP is different than LCL,ARG,THIS,THAT bc it does not store a pointer to ram, rather it's just 5-12.
      elif("local" == segment):
        #get value at top of stack, store in memory[memory[LCL+index]]
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the offset in D
          "@LCL\n" #get ram[...] in A, so M points to address of ... (local, arg, etc.)
          "A=M+D\n" #point to the address of the desired value
          "D=M\n" #D stores the desired value

          "@SP\n" #point to SP to get address in M (1past top of current stack)
          "A=M\n" #point to 1past top of current stack
          "M=D\n" #store the desired value (in D) onto the stack
          "@SP\n" #get ready to increment stack pointer
          "M=M+1\n") #increment it
      elif("argument" == segment):
        #get value at top of stack, store in memory[memory[ARG+index]]
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the offset in D
          "@ARG\n" #get ram[...] in A, so M points to address of ... (local, arg, etc.)
          "A=M+D\n" #point to the address of the desired value
          "D=M\n" #D stores the desired value

          "@SP\n" #point to SP to get address in M (1past top of current stack)
          "A=M\n" #point to 1past top of current stack
          "M=D\n" #store the desired value (in D) onto the stack
          "@SP\n" #get ready to increment stack pointer
          "M=M+1\n") #increment it
      elif("this" == segment):
        #get value stored in memory[memory[THIS+index]]
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the offset in D
          "@THIS\n" #get ram[...] in A, so M points to address of ... (local, arg, etc.)
          "A=M+D\n" #point to the address of the desired value
          "D=M\n" #D stores the desired value

          "@SP\n" #point to SP to get address in M (1past top of current stack)
          "A=M\n" #point to 1past top of current stack
          "M=D\n" #store the desired value (in D) onto the stack
          "@SP\n" #get ready to increment stack pointer
          "M=M+1\n") #increment it
      elif("that" == segment):
        #get value stored in memory[memory[THAT+index]]
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the offset in D
          "@THAT\n" #get ram[...] in A, so M points to address of ... (local, arg, etc.)
          "A=M+D\n" #point to the address of the desired value
          "D=M\n" #D stores the desired value

          "@SP\n" #point to SP to get address in M (1past top of current stack)
          "A=M\n" #point to 1past top of current stack
          "M=D\n" #store the desired value (in D) onto the stack
          "@SP\n" #get ready to increment stack pointer
          "M=M+1\n") #increment it
      elif("pointer" == segment):
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the offset in D
          "@THIS\n" #get ram[...] in A (could also use R3 here, a synonym.)
          "A=A+D\n" #point to the address of the desired value (THIS or THAT, essentially, in the case of pointer)
          "D=M\n" #D stores the desired value

          "@SP\n" #point to SP to get address in M (1past top of current stack)
          "A=M\n" #point to 1past top of current stack
          "M=D\n" #store the desired value (in D) onto the stack
          "@SP\n" #get ready to increment stack pointer
          "M=M+1\n") #increment it
      elif("temp" == segment): #temp is R5-R12
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the offset in D
          "@R5\n" #get ram[...] in A
          "A=A+D\n" #point to the address of the desired value
          "D=M\n" #D stores the desired value

          "@SP\n" #point to SP to get address in M (1past top of current stack)
          "A=M\n" #point to 1past top of current stack
          "M=D\n" #store the desired value (in D) onto the stack
          "@SP\n" #get ready to increment stack pointer
          "M=M+1\n") #increment it
      elif("static" == segment):
        #note: "each static variable j in file Xxx.vm is translated into the assembly symbol Xxx.j"
        towrite=("@"+static_namespace+"."+str(index)+"\n"
          "D=M\n" #store value of static variable in D
          "@SP\n" #point at the stack pointer (this assembly language isn't confusing, is it?)
          "A=M\n" #point to newtop of stack
          "M=D\n" #store the value of the static variable at newtop
          "@SP\n" #go back to stack pointer to increment it
          "M=M+1\n")




    elif("pop" == command):
      if("local" == segment):
        #get value at top of stack, store in memory[memory[LCL+index]]
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the constant in D
          "@LCL\n" #get ram[1] in A, so M points to address of local
          "D=M+D\n" #D stores the address of the desired value
          "@R14\n" #M[R14] will be used (R13-R15 are general-purpose, so why not?)
          "M=D\n" #put the desired address in M[R14]
          "@SP\n" #get the value at the top of the stack
          "M=M-1\n" #decrement the stack pointer
          "A=M\n" #get M[SPnew] by pointing
          "D=M\n" #put value previously at top of stack in D
          "@R14\n" #retrieve desired address
          "A=M\n" #point to desired address
          "M=D\n") #M[desired address] <-- desired value (D, from previous top of stack)
      elif("argument" == segment):
        #get value at top of stack, store in memory[memory[ARG+index]]
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the constant in D
          "@ARG\n" #get ram[...] in A, so M points to address of ...
          "D=M+D\n" #D stores the address of the desired value
          "@R14\n" #M[R14] will be used (R13-R15 are general-purpose, so why not?)
          "M=D\n" #put the desired address in M[R14]
          "@SP\n" #get the value at the top of the stack
          "M=M-1\n" #decrement the stack pointer
          "A=M\n" #get M[SPnew] by pointing
          "D=M\n" #put value previously at top of stack in D
          "@R14\n" #retrieve desired address
          "A=M\n" #point to desired address
          "M=D\n") #M[desired address] <-- desired value (D, from previous top of stack)
      elif("this" == segment):
        #get value stored in memory[memory[THIS+index]]
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the constant in D
          "@THIS\n" #get ram[...] in A, so M points to address of ...
          "D=M+D\n" #D stores the address of the desired value
          "@R14\n" #M[R14] will be used (R13-R15 are general-purpose, so why not?)
          "M=D\n" #put the desired address in M[R14]
          "@SP\n" #get the value at the top of the stack
          "M=M-1\n" #decrement the stack pointer
          "A=M\n" #get M[SPnew] by pointing
          "D=M\n" #put value previously at top of stack in D
          "@R14\n" #retrieve desired address
          "A=M\n" #point to desired address
          "M=D\n") #M[desired address] <-- desired value (D, from previous top of stack)
      elif("that" == segment):
        #get value stored in memory[memory[ARG+index]]
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the constant in D
          "@THAT\n" #get ram[...] in A, so M points to address of ...
          "D=M+D\n" #D stores the address of the desired value
          "@R14\n" #M[R14] will be used (R13-R15 are general-purpose, so why not?)
          "M=D\n" #put the desired address in M[R14]
          "@SP\n" #get the value at the top of the stack
          "M=M-1\n" #decrement the stack pointer
          "A=M\n" #get M[SPnew] by pointing
          "D=M\n" #put value previously at top of stack in D
          "@R14\n" #retrieve desired address
          "A=M\n" #point to desired address
          "M=D\n") #M[desired address] <-- desired value (D, from previous top of stack)
      elif("temp" == segment):
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the constant in D
          "@R5\n" #get ram[...] in A, so M points to address of ...
          "D=A+D\n" #D stores the address of the desired value
          "@R14\n" #M[R14] will be used (R13-R15 are general-purpose, so why not?)
          "M=D\n" #put the desired address in M[R14]
          "@SP\n" #get the value at the top of the stack
          "M=M-1\n" #decrement the stack pointer
          "A=M\n" #get M[SPnew] by pointing
          "D=M\n" #put value previously at top of stack in D
          "@R14\n" #retrieve desired address
          "A=M\n" #point to desired address
          "M=D\n") #M[desired address] <-- desired value (D, from previous top of stack)
      elif("pointer" == segment):
        towrite = ("@"+str(index)+"\n"
          "D=A\n" #store the constant in D
          "@THIS\n" #get ram[...] in A, so M points to address of ...
          "D=A+D\n" #D stores the address of the desired value
          "@R14\n" #M[R14] will be used (R13-R15 are general-purpose, so why not?)
          "M=D\n" #put the desired address in M[R14]
          "@SP\n" #get the value at the top of the stack
          "M=M-1\n" #decrement the stack pointer
          "A=M\n" #get M[SPnew] by pointing
          "D=M\n" #put value previously at top of stack in D
          "@R14\n" #retrieve desired address
          "A=M\n" #point to desired address
          "M=D\n") #M[desired address] <-- desired value (D, from previous top of stack)
      elif("static" == segment):
        #note: "each static variable j in file Xxx.vm is translated into the assembly symbol Xxx.j"
        towrite = ("@SP\n"
          "M=M-1\n" #decrement stack pointer
          "A=M\n" #get M[SPnew] by pointing there
          "D=M\n" #store topstack value to D
          "@"+static_namespace+"."+str(index)+"\n" #point to the static variable
          "M=D\n") #store the popped value in the static variable
          
    self.fout.write(towrite) #write the constructed assembly to file.

  def close(self):
    self.fout.close()
