#we will implement the parser as a class, similar to the assembly parser.

class Parser:

  AL_CMDs = ["add","sub","neg","eq","gt","lt","and","or","not"]
  
  def __init__(self, filename):
    #once again, instead of having the file eternally open as a stream, let's just read it all at once.  simpler I think.
    f_vm = open(filename, 'r')
    self.lines_vm = f_vm.readlines()
    f_vm.close()
    self.total_vm_lines = len(self.lines_vm)
    self.vm_line = -1  


  def hasMoreCommands(self):
    if(self.vm_line >= self.total_vm_lines - 1):
      return False
    else:
      return True

  
  def advance(self):
    if(self.hasMoreCommands()):
      self.vm_line = self.vm_line + 1
      self.current_vm_line = self.lines_vm[self.vm_line]
      self.current_vm_line = (self.current_vm_line.split('//')[0]).strip() #get rid of comments & excess white space
      self.current_vm_cmd = self.current_vm_line.split(' ')
     
    else:
      print("error: called advance() but hasMoreCommands() is false") 

   
  def commandType(self):

    cmd = self.current_vm_cmd[0]
    
    if("push" == cmd):
      return "C_PUSH"
    elif("pop" == cmd):
      return "C_POP"
    elif("label" == cmd):
      return "C_LABEL"
    elif("goto" == cmd):
      return "C_GOTO"
    elif("if-goto" == cmd):
      return "C_IF"
    elif("function" == cmd):
      return "C_FUNCTION"
    elif("call" == cmd):
      return "C_CALL"
    elif("return" == cmd):
      return "C_RETURN"
    elif(cmd in self.AL_CMDs):
      return "C_ARITHMETIC"

    else:
      #instead of printing here, we'll just make it default behavior to return None (no return) if there is no valid command
      #print("error: called commandType but there is no valid command")
      pass

 
  def arg1(self):
    cmdT = self.commandType()
    if(cmdT == "C_ARITHMETIC"):
      return self.current_vm_cmd[0]
    else:
      if(len(self.current_vm_cmd) > 1):
        return self.current_vm_cmd[1]
      else:
        print("called arg1 when len(self.current_vm_cmd) <= 1")

  def arg2(self):
    cmdT = self.commandType()
    if(cmdT in ["C_PUSH","C_POP","C_FUNCTION","C_CALL"]):
      if(len(self.current_vm_cmd) > 2):
        return int(self.current_vm_cmd[2])
      else:
        print("called arg2 when len(self.current_vm_cmd) <= 2")
    else:
      print("called arg2 with wrong command type: " + cmdT)
