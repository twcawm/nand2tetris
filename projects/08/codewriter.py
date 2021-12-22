class CodeWriter:

  def __init__(self, filename): #this filename is of the form *.asm (something[:-4])
    self.fout = open(filename, "w")
    self.labelCount = 0
    self.call_count = 0
    self.functionName = "default_fn"


  def newLabel(self):
    self.labelCount = self.labelCount + 1
    return "LABEL"+str(self.labelCount).zfill(3)
    


  def setFileName(self, filename): #this filename is of the form *.vm (something[:-3])
    if(filename.endswith(".vm")):
      self.static_namespace = filename[:-3]
      self.static_namespace = self.static_namespace.split('/')[-1] #we don't want full path, just final name
    else:
      print("error in setFileName: does not end with '.vm'")

  def writeLabel(self, label):
    towrite = "("+self.functionName+"$"+label+")\n" #has to include functionName
    self.fout.write(towrite) #write the constructed assembly to file.
  
  def writeGoto(self, label):
    towrite = ("@"+self.functionName+"$"+label+"\n" #has to include functionName
      "0;JMP\n")
    self.fout.write(towrite) #write the constructed assembly to file.

  def writeIf(self, label):
    towrite = ("@SP\n"
      "M=M-1\n" #decrement stack pointer
      "A=M\n" #point to that value
      "D=M\n" #store it in D
      "@"+self.functionName+"$"+label+"\n" #has to include functionName
      "D;JNE\n") #jump if the value is not equal to zero
    self.fout.write(towrite) #write the constructed assembly to file.

  def writeCall(self, functionName, numArgs):
    self.call_count = self.call_count + 1
    returnSymbol = functionName+"_RETURN_"+str(self.call_count)

    towrite = (
      "@"+returnSymbol+"\n" #push the return address to the stack
      "D=A\n" # (store return address in D)
      "@SP\n" # point to 1past topstack
      "A=M\n" 
      "M=D\n" # store desired value at that location
      "@SP\n"
      "M=M+1\n" #increment stack pointer

      "@LCL\n" # push LCL to the stack
      "D=M\n"
      "@SP\n"
      "A=M\n"
      "M=D\n"
      "@SP\n"
      "M=M+1\n" #increment stack pointer

      "@ARG\n" # push ARG to the stack
      "D=M\n"
      "@SP\n"
      "A=M\n"
      "M=D\n"
      "@SP\n"
      "M=M+1\n" #increment stack pointer

      "@THIS\n" # push THIS to the stack
      "D=M\n"
      "@SP\n"
      "A=M\n"
      "M=D\n"
      "@SP\n"
      "M=M+1\n" #increment stack pointer

      "@THAT\n" # push THAT to the stack
      "D=M\n"
      "@SP\n"
      "A=M\n"
      "M=D\n"
      "@SP\n"
      "M=M+1\n" #increment stack pointer

      #now we have to compute and set set ARG to SP - n - 5
      "@"+str(numArgs)+"\n"
      "D=A\n"
      "@5\n"
      "D=D+A\n" #D is (n+5)
      "@SP\n"
      "D=M-D\n" #store SP - n - 5 in D
      "@ARG\n"
      "M=D\n" #store that in Arg

      #now we have to set LCL to SP
      "@SP\n"
      "D=M\n"
      "@LCL\n"
      "M=D\n"

      "@"+functionName+"\n"
      "0;JMP\n" #unconditional jump to wherever the function code is

      "("+returnSymbol+")\n"
    )
    self.fout.write(towrite) #write the constructed assembly to file.

  def writeReturn(self):
    towrite = (
      "@LCL\n"
      "D=M\n" #put LCL in D
      "@R13\n" #put this value in a temporary var, "FRAME" (R13 is temporary FRAME)
      "M=D\n"

      "@5\n" #about to do RET = m(FRAME - 5)
      "A=D-A\n" #D is holding FRAME, A now holds FRAME-5
      "D=M\n" #store return address
      "@R15\n" #use R15 to store return address
      "M=D\n"

      #now we pop a value (THE RETURN VALUE!) into ARG
      #(the next set of commands will place this at the top of the caller stack)
      "@SP\n" 
      "M=M-1\n"
      "A=M\n"
      "D=M\n"
      "@ARG\n"
      "A=M\n" #point to addres stored by ARG
      "M=D\n" #store the popped value in that address

      "D=A\n" #SP = ARG + 1.  this moves SP back to caller stack.
      "@SP\n"
      "M=D+1\n"

      "@R13\n" #put m(FRAME-1) into THAT.  recall @R13 stores FRAME
      "M=M-1\n" #(decrement - now, m[R13] is FRAME-1)
      "A=M\n"
      "D=M\n"
      "@THAT\n"
      "M=D\n"

      "@R13\n" #put m(FRAME-2) into THIS.  recall @R13 stores FRAME
      "M=M-1\n" #decrement again: now, m[R13] is FRAME-2
      "A=M\n"
      "D=M\n"
      "@THIS\n"
      "M=D\n"
   
      "@R13\n" #put m(FRAME-3) into ARG
      "M=M-1\n" #decrement again: now, m[R13] is FRAME-3
      "A=M\n"
      "D=M\n"
      "@ARG\n"
      "M=D\n"

      "@R13\n" #put m(FRAME-4) into LCL
      "M=M-1\n" #decrement again: now, m[R13] is FRAME-4
      "A=M\n"
      "D=M\n"
      "@LCL\n"
      "M=D\n"

      "@R15\n" #point to where return address is stored
      "A=M\n" #load return address
      "0;JMP\n" #unconditional jump to return address.  all is well.
    )
    self.fout.write(towrite) #write the constructed assembly to file.

  def writeFunction(self, functionName, numLocals):
    self.functionName = functionName #update functionName field
    init_loop = functionName + "_INIT_LOOP"
    init_end = functionName + "_INIT_END"
    towrite = (
      "(" + functionName + ")\n"
      "@"+str(numLocals)+"\n"
      "D=A\n"
      "@R14\n" #use R14 as a temporary var
      "M=D\n"  #to store the number of local vars

      "("+init_loop+")\n" #begin init loop
      "@"+init_end+"\n"
      "D;JEQ\n" #if D is 0, go to end of init loop
    
      #our job is to initialize function locals by pushing 0 to stack.
      "@0\n" #point to stack pointer... except not.  we're just using 0 as a value.
      "D=A\n" #store 0 in D
      "@SP\n" #point to stack pointer... for real this time (don't you love Hack assembly?)
      "A=M\n" #point to 1past top of stack
      "M=D\n" #set that value to 0
      "@SP\n" #increment stack pointer to finish push.
      "M=M+1\n"
      "@R14\n" #decrement the number of temporary vars left to initialize
      "M=M-1\n"
      "D=M\n" #also store the #locals left to initialize in D (that's what we're using to terminate)
      "@"+init_loop+"\n"
      "0;JMP\n"
      "("+init_end+")\n"
    )
    self.fout.write(towrite) 
      

  def writeInit(self): 
    towrite = ("@256\n"
      "D=A\n"
      "@SP\n"
      "M=D\n")
    self.fout.write(towrite)

    self.writeCall("Sys.init",0)
    #we're basically just using the suggested implementation.
    #not sure whether there is any error checking or things to handle from Sys.init.
    #for now we will leave it alone.


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
        towrite=("@"+self.static_namespace+"."+str(index)+"\n"
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
          "@"+self.static_namespace+"."+str(index)+"\n" #point to the static variable
          "M=D\n") #store the popped value in the static variable
          
    self.fout.write(towrite) #write the constructed assembly to file.

  def close(self):
    self.fout.close()
