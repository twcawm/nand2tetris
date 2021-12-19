import re

# implementation of suggested Parser API
# it seems most natural to make the Parser a class, since it has some encapsulated state and methods that change the state

class Parser:

  def __init__(self, fname):
    f_asm = open(fname, 'r')
    self.lines_asm = f_asm.readlines()
    f_asm.close() # I don't feel like dealing with an open file in my class.  probably easier to just read into lines_asm and deal with that in memory.  could update this later if we wanted to handle exceptionally large files or streams.
    self.asm_line = -1 #I think it will make sense to track both what line we're at in the asm file, and what line we're at in the Hack file / output / ROM
    self.hack_line = -1 #not sure yet if initializing these at 0 is correct, will think more when we get there
    self.has_read_asm_line = False #this is just to make the line convention crystal clear: this is False if we haven't read the current asm_line and True after we read it.  I might actually take this out if I find out that it's redundant.
    

  def hasMoreCommands(self): #a slight misnomer - we will treat this as "hasMoreLines" as we do not truly know whether the next line will be a "command" or not
    if(self.asm_line >= len(self.lines_asm)-1): #if len is 10 && asm_line=9, we have no more lines to read.  so the -1 is needed.
      return False 
    else:
      return True

  def advance(self):
    if(self.hasMoreCommands()):
      self.asm_line = self.asm_line + 1 #initial: asm_line initialized to -1, so this works for initial advance() to read the very first line
      self.current_asm_line = self.lines_asm[self.asm_line]
      self.current_asm_line = self.current_asm_line.split('//')[0] #get rid of comments
      self.current_asm_line = ''.join(self.current_asm_line.split()) #get rid of annoying spaces and newline
      if(self.commandType() == "A_COMMAND" or self.commandType() == "C_COMMAND"):
        self.hack_line = self.hack_line + 1 #thus, we keep track of the ROM addresses needed for the labels
        #hack_line is -1 before any hack commands have been read.  it is 0 at the first hack command (ROM address)
    else:
      print("error: called advance() but hasMoreCommands() is false")

  def commandType(self):
    if('@' in self.current_asm_line):
      return "A_COMMAND"
    elif(('=' in self.current_asm_line) or (';' in self.current_asm_line)):
      return "C_COMMAND"
    elif(('(' in self.current_asm_line) and (')' in self.current_asm_line)):
      if(self.current_asm_line.index(')') > self.current_asm_line.index('(')):
        return "L_COMMAND"
      else:
        print("( came after ) - possibly malformed L_COMMAND?")
    else:
      return None #important: our convention is to return None when the assembly line does not correspond to any command (this could be a comment, white space, etc.)
 
  def symbol(self):
    #could use regex to do this.  but instead we'll just manually parse using split()
    cmdT = self.commandType()
    if(cmdT == "A_COMMAND"):
      ret = self.current_asm_line.split('@')[1]    
      #could add better error checking here
      ret.strip()
      return ret
    elif(cmdT == "L_COMMAND"):
      ret = self.current_asm_line.split('(')[1]
      ret = ret.split(')')[0]
      ret.strip()
    else:
      print("error: symbol() called on non-A or C command.")

  def dest(self):
    cmdT = self.commandType()
    if(cmdT == "C_COMMAND" and '=' in self.current_asm_line):
      ret = self.current_asm_line.split('=')[0]
    else:
      ret = '' #currently we just return empty string.  could have possibly better error handling (for the case when not a C_COMMAND, for example)
    return ret
 
  def comp(self):
    cmdT = self.commandType()
    if(cmdT == "C_COMMAND"):
      tmp = re.sub(r'.*=',"",self.current_asm_line)
      ret = re.sub(r';.*',"",tmp)
      ret.strip()
    else:
      ret = '' #currently we just return empty string.  could have possibly better error handling (for the case when not a C_COMMAND, for example)
    return ret

  def jump(self):
    cmdT = self.commandType()
    if(cmdT == "C_COMMAND" and ';' in self.current_asm_line):
      tmp = re.sub(r'.*;',"",self.current_asm_line)
      tmp.strip()
    else:
      tmp = ''
    return tmp
