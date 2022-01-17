class SymbolTable:

  def __init__(self):
    self.class_scope = {} #empty dict ("hashmap") for class scope
    self.subroutine_scope = {}
    self.set_scope_class() #set current_scope to class
    #counters for var, arg, field, static
    self.count_var = 0
    self.count_arg = 0
    self.count_field = 0
    self.count_static = 0
    #counters for flow control labels
    self.count_if = 0
    self.count_while = 0

  def startSubroutine(self):
    self.subroutine_scope = {}
    self.count_var = 0
    self.count_arg = 0

  def define(self,id_name, id_type, id_kind): #id_type is static, field, arg, var
    if(id_kind == "field"):
      self.class_scope[id_name] = (id_kind, id_type, self.count_field)
      self.count_field += 1
    elif(id_kind == "static"):
      self.class_scope[id_name] = (id_kind, id_type, self.count_static)
      self.count_static += 1
    elif(id_kind == "arg"): #is a formal parameter (the book calls it an "argument" but i think more conventionally this is known as a 'formal parameter' - the variable that holds the value passed in)
      self.subroutine_scope[id_name] = (id_kind, id_type, self.count_arg)
      self.count_arg += 1
    elif(id_kind == "var"): 
      self.subroutine_scope[id_name] = (id_kind, id_type, self.count_var)
      self.count_var += 1
  
  '''
  def varCount(self,id_kind):
    if(id_kind == "field"):
      return self.count_field
    if(id_kind == "static"):
      return self.count_static
    if(id_kind == "arg"):
      return self.count_arg
    if(id_kind == "var"):
      return self.count_var
  '''
  def varCount(self, id_kind):
    if(self.current_scope == "subroutine"):
      l_globals = [meta for (varname, meta) in self.subroutine_scope.items() if meta[0] == id_kind]
      return len(l_globals)
    else:
      return self.classCount(id_kind)

  def classCount(self, id_kind): #specifically the class/global variables of this kind
    l_globals = [meta for (varname, meta) in self.class_scope.items() if meta[0] == id_kind]
    return len(l_globals)

  def kindOf(self,id_name): #in a more advanced language this would be a nested search starting from "current scope".  
                       #but here, we only ever have 2 scopes maximum (subroutine and class)
    if(current_scope == "subroutine" and id_name in self.subroutine_scope):
      return self.subroutine_scope[id_name][0] #only look in subroutine if the current scope is subroutine.
        #(not sure if checking that is needed or not, but better to be safe
    elif(id_name in self.class_scope):
      return self.class_scope[id_name][0]
 
  def typeOf(self,id_name): 
    if(current_scope == "subroutine" and id_name in self.subroutine_scope):
      return self.subroutine_scope[id_name][1] #only look in subroutine if the current scope is subroutine.
    elif(id_name in self.class_scope):
      return self.class_scope[id_name][1]

  def indexOf(self,id_name): 
    if(current_scope == "subroutine" and id_name in self.subroutine_scope):
      return self.subroutine_scope[id_name][2] #only look in subroutine if the current scope is subroutine.
    elif(id_name in self.class_scope):
      return self.class_scope[id_name][2]

  def set_scope_class(self):
    self.current_scope = "class"
  def set_scope_subroutine(self):
    self.current_scope = "subroutine"
