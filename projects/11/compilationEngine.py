import vmWriter

class CompilationEngine:

  l_decl_subroutine = ["constructor", "method", "function"]
  l_decl_classvar = ["static", "field"]
  l_statement = ["if", "do", "let", "while", "return"]

  l_unary = ['-','~']
  l_binary = ['+', '-', '*', '/', '&', '|', '<', '>', '=', '&lt;', '&gt;', '&amp;']
    #had to fix this to include the escaped versions since we do that in tokenizer
  l_kwd_const = ['true','false','null','this']

  def __init__(self, tokenizer, fout): #construct with an already-formed tokenizer, and an already opened file
    self.tok = tokenizer
    self.fout = fout
    self.vm_writer = vmWriter.VMWriter(fout)
    self.symbol_table = symbolTable.SymbolTable()

    self.class_name = ""
    self.subroutine_name = ""

    #self.element_stack = [] #only needed for XML phase
    #self.indents = "" #only needed for XML phase

  #only needed for XML phase
  '''
  def write_nonterm_begin(self, element):
    self.fout.write(self.indents + "<" + element + ">\n")
    self.element_stack.append(element)
    self.increase_indents()
  def write_nonterm_end(self):
    element = self.element_stack.pop()
    self.decrease_indents()
    self.fout.write(self.indents + "</" + element + ">\n")
  def write_terminal(self):
    tokenType, tokenValue = self.tok.current_token #current_token is a type of tokentype, value
    tokenType = self.tok.d_lex[tokenType] #get the XML form
    if(tokenType == "stringConstant"): #special case for string constant, annoying.
      tokenValue = tokenValue[1:-1] #get rid of the '"'
    self.fout.write(self.indents + "<" + tokenType + "> " + tokenValue + " </" + tokenType + ">\n")
 
  def increase_indents(self):
    self.indents += "  " 
  def decrease_indents(self):
    self.indents = self.indents[:-2]
  '''

  def cadvance(self): #modified form of cadvance: we do not want to write, but sometimes we need to capture tokens
    self.tok.advance()
    return self.tok.current_token
    #self.write_terminal() #writes the current terminal token

  def compileClass(self):
    #this should be the first compile method called per compilation unit (file (one class per file)) 
    #self.write_nonterm_begin("class")
    self.cadvance() #consume "class"
    if(self.tok.current_token[1] != "class"):
      print('error: expected "class" as first token in compileClass') #rudimentary error handling
    self.class_name = self.cadvance() #capture class name
    if(self.tok.current_token[0] != "IDENTIFIER"):
      print('error: expected identifier after "class"')
    self.cadvance()
    if(self.tok.current_token[1] != "{"):
      print('error: expected {')
    
    while(self.tok.hasMoreTokens() and (self.tok.lookAhead()[1] in self.l_decl_classvar)): #if next token begins class var declaration
      self.compileClassVarDec()
    while(self.tok.hasMoreTokens() and (self.tok.lookAhead()[1] in self.l_decl_subroutine)): #if next token begins class var declaration
      self.compileSubroutine()

    self.cadvance() #consume }
    if(self.tok.current_token[1] != "}"):
      print('error: expected } in compileClass')
    #self.write_nonterm_end()
    self.fout.close() #we are done (note: probably we should actually close this in the calling program, not here.  possible improvement.)
   

  def compileClassVarDec(self):
    #self.write_nonterm_begin("classVarDec")
    lkind = self.cadvance()[1] #"static" or "field"
    if(self.tok.current_token[1] not in self.l_decl_classvar):
      print('error: expected "static" or "field"') #in retrospect this shouldn't be necessary since we only call this when this condition is satisfied.  could delete later.
    ltype = self.cadvance()[1] #var type - we could add better error checking later.
    lname = self.cadvance()[1] #var name
    self.symbol_table.define(lname, ltype, lkind)
    while(self.tok.lookAhead()[1] == ","):
      self.cadvance() # consume ','
      lname = self.cadvance()[1] # consume name
      if(self.tok.current_token[0] != "IDENTIFIER"):
        print('error: expected identifier (class variable name)')
      self.symbol_table.define(lname, ltype, lkind) #all vars in same declaration list have same type, kind
    self.cadvance() # consume ";"
    if(self.tok.current_token[1] != ";"):
      print('error: expected ; but got ' + self.tok-current_token[1])
    #self.write_nonterm_end()

  def compileSubroutine(self):
    #self.write_nonterm_begin("subroutineDec")
    ftype = self.cadvance()[1] #consume  "constructor", "method", "function"
    self.cadvance() #consume return type or 'void'
    self.subroutine_name = self.class_name + "." + self.cadvance()[1] #consume subroutine name 
    self.symbol_table.startSubroutine(self.subroutine_name)
    self.symbol_table.set_scope_subroutine() #ensure symbol table scope is set to 'subroutine'
    self.cadvance() #consume (
    if(self.tok.current_token[1] != "("):
      print('error: expected ( in compileSubroutine')
    self.compileParameterList(ftype)
    self.cadvance() #consume ) 
    self.compileSubroutineBody(ftype) #separate this out as a function for a bit of sanity
    #self.write_nonterm_end()
      
  def compileParameterList(self, ftype): #need to know whether it's a method or not
    #self.write_nonterm_begin("parameterList")
    if(ftype == "method"):
      self.symbol_table.define("this", "self", "arg") #name=this, type=self, kind=arg.  refers to current object.
    while(self.tok.lookAhead()[1] != ")"):
      ptype = self.cadvance()[1] #consume parameter type
      pname = self.cadvance()[1] #consume parameter name
      self.symbol_table.define(pname, ptype, "arg")
      if(self.tok.lookAhead()[1] == ","):
        self.cadvance() #consume comma and loop around 
    #self.write_nonterm_end() #note: we leave the ")" as the next token.  we did not consume it.

  def compileSubroutineBody(self, ftype):
    #self.write_nonterm_begin("subroutineBody")
    self.cadvance() #consume {
    if(self.tok.current_token[1] != "{"):
      print('error: expected { for subroutine body')
    while(self.tok.lookAhead()[1] == 'var'):
      self.compileVarDec()
    count_vars = self.symbol_table.varCount("var")
    self.vm_writer.writeFunction(self.subroutine_name, count_vars)
    self.load_pointer(ftype) #todo: check this
    self.compileStatements()
    self.cadvance() #consume }
    if(self.tok.current_token[1] != "}"):
      print('error: expected } to end subroutine body')
    self.symbol_table.set_scope_class() #exit subroutine scope
    #self.write_nonterm_end()

  def load_pointer(self, fype):
    if(ftype == "method"): #code for setting "this" to refer to (hold the address of) the passed object
      self.vm_writer.writePush("argument", 0)
      self.vm_writer.writePop("pointer", 0)
    if(ftype == "constructor"): #code for allocating memory for the object's fields!
      count_globals = self.symbol_table.classCount("field")
      self.writer.writePush("constant", count_globals)
      self.writer.writeCall("Memory.alloc", 1) #convention from book
      self.writer.writePop("pointer", 0) #result: "this" refers to the newly constructed object

  def compileVarDec(self):
    #self.write_nonterm_begin("varDec")
    vkind = self.cadvance()[1] #consume 'var'
    vtype = self.cadvance()[1] #consume type 
    vname = self.cadvance()[1] #consume name 
    self.symbol_table.define(vname, vtype, vkind)
    while(self.tok.lookAhead()[1] == ","): #handles case of list of names
      self.cadvance() #consume ","
      vname = self.cadvance() #consume name
      self.symbol_table.define(vname, vtype, vkind) #same type & kind in same decl list
    self.cadvance() #consume ;
    if(self.tok.current_token[1] != ";"):
      print('error: expected ; end of compileVarDec')
    #self.write_nonterm_end()
  
  def compileStatements(self): #statements: statement* ;   statement: let, do , if, while, return
    #self.write_nonterm_begin("statements")
    while(self.tok.lookAhead()[1] in self.l_statement):
      if(self.tok.lookAhead()[1] == "if"):
        self.compileIf()
      if(self.tok.lookAhead()[1] == "do"):
        self.compileDo()
      if(self.tok.lookAhead()[1] == "let"):
        self.compileLet()
      if(self.tok.lookAhead()[1] == "while"):
        self.compileWhile()
      if(self.tok.lookAhead()[1] == "return"):
        self.compileReturn()
    #self.write_nonterm_end()

  def compileIf(self): #there are a few way of ordering the blocks.  we do it here a different way than the book does.
    #self.write_nonterm_begin("ifStatement")
    self.cadvance() #consume if
    self.cadvance() #consume (
    self.compileExpression() #now, the result of the if condition is on the stack.
    self.cadvance() #consume )
    count_if = self.symbol_table.count_if
    self.symbol_table.count_if += 1
    self.vm_writer.writeIf('LTRUE'+str(count_if)) #go to this label if true
    self.vm_writer.writeGoto('LFALSE'+str(count_if)) #go to this label unconditionally (if false)
    self.vm_writer.writeLabel('LTRUE'+str(count_if)) #the block of code for the if body
    self.cadvance() #consume {
    self.compileStatements()
    self.cadvance() #consume }
    if(self.tok.lookAhead()[1] == "else"):
      self.vm_writer.writeGoto("LEND"+str(count_if)) #if we reach this , we were in if - go to end to skip the else block.
      self.vm_writer.writeLabel("LFALSE"+str(count_if)) #else, here's the else block code.
      self.cadvance() #consume the else
      self.cadvance() #consume the {
      self.compileStatements()
      self.cadvance() #consume the }
      self.vm_writer.writeLabel("LEND"+str(count_if))
    else:
      self.vm_writer.writeLabel("LFALSE"+str(count_if)) #no else block.  just go to end of if block if condition false.
    #self.write_nonterm_end()

  def compileDo(self):
    #self.write_nonterm_begin("doStatement")
    base_name = ""
    adot_name = "" #possible name after dot
    full_name = "" #name of vm function to do
    self.cadvance() # consume do

    count_locals = 0 #todo: understand this better
 
    #subroutine call:
    base_name = self.cadvance()[1] #consume subroutine name OR class/var name (constructor/method)
    if(self.tok.lookAhead()[1] == "."): #it is a class/var.constructor/method call
      #IF IT's a VARIABLE (in scope), get its type (classname) and call classname.method() etc
      #  if not, then it's likely classname.method() directly - just call that.
      self.cadvance() # consume the . symbol
      adot_name = self.cadvance()[1] # consume the subroutine name 
      #we need to decide whether we have this object type in scope:
      if((self.symbol_table.current_scope == "subroutine" and base_name in self.symbol_table.subroutine_scope) or
         (base_name in self.symbol_table.class_scope)):
        #if we have it in scope, write code to push it to stack
        self.write_push(base_name, adot_name) #handles this using kindOf(base_name)
        full_name = self.symbol_table.typeOf(base_name) + "." + adot_name
        count_locals = count_locals + 1
      else:
        #if we don't have it in scope, then all we can do is assume we desire to "call basename.adotname" 
        full_name = base_name + "." + adot_name
    else:
      self.vm_writer.writePush('pointer', 0)
      count_locals += 1
      full_name = self.class_name + "." + first_name
    self.cadvance() #consume (
    count_locals += self.compileExpressionList()
    self.vm_writer.writeCall(full_name, count_locals)
    self.cadvance() #consume )
    #end subroutine call
 
    self.vm_writer.writePop("temp", 0) 
    self.cadvance() # consume ;
    if(self.tok.current_token[1] != ";"):
      print('error: expected ; end of compileDo')
    #self.write_nonterm_end()

  def compileLet(self):
    #self.write_nonterm_begin("letStatement")
    self.cadvance() #consume let
    vname = self.cadvance()[1] #consume variable name
    is_array = False
    if(self.tok.lookAhead()[1] == "["): # it is an array index
      is_array = True
      self.cadvance() #consume the [
      self.compileExpression()
      self.cadvance() #consume the ]

      self.compileArrayIndex(vname)
    self.cadvance() #consume the =
    if(self.tok.current_token[1] != "="):
      print('error: expected "=" in Let statement')
    self.compileExpression()
    if(is_array):
      self.vm_writer.writePop("temp",0)
      self.vm_writer.writePop("pointer",1)
      self.vm_writer.writePush("temp", 0)
      self.vm_writer.writePop("that", 0)
    else:
      self.write_pop(vname)
    self.cadvance() #consume ;
    if(self.tok.current_token[1] != ";"):
      print('error: expected ; end of compileLet')
    #self.write_nonterm_end()

  def compileArrayIndex(self, vname)
    d_fullnames = {"var":"local", "arg":"argument"}
    if((self.symbol_table.current_scope == "subroutine" and vname in self.symbol_table.subroutine_scope) or
         (vname in self.symbol_table.class_scope)): #if vname in current scope
      kind = self.symbol_table.kindOf(vname)
      self.vm_writer.writePush(d_fullnames[kind], self.symbol_table.indexOf(vname))
    else:
      kind = self.symbol_table.kindOf(vname)
      if(kind == "static"):
        self.vm_writer.writePush("static", self.symbol_table.indexOf(vname))
      else:
        self.vm_writer.writePush("this", self.symbol_table.indexOf(vname))
    self.vm_writer.writeArithmetic("add")

  def compileWhile(self): #there are various ways of ordering the blocks/labels.  here we use the one straight from the book!
    #self.write_nonterm_begin("whileStatement")
    count_while = self.symbol_table.count_while
    self.symbol_table.count_while += 1
    self.vm_writer.writeLabel('WHILEBLOCK' + str(count_while))
    self.cadvance() #consume the 'while'
    self.cadvance() #consume (
    self.compileExpression()
    self.vm_writer.writeArithmetic('not') #must negate the while condition in order for this order to be correct
    self.vm_writer.writeIf('ENDWHILE' + str(count_while)) #if not while cond, then break to label after block!
    self.cadvance() #consume )
    self.cadvance() #consume {
    self.compileStatements()
    self.vm_writer.writeGoto('WHILEBLOCK' + str(count_while)) #reached end of while block - loop back to top
    self.vm_writer.writeLabel('ENDWHILE' + str(count_while)) 
    self.cadvance() #consume }
    if(self.tok.current_token[1] != "}"):
      print('error: expected } end of compileWhile')
    #self.write_nonterm_end()
 
  #todo: revise the way we're testing for "next thing is an expression" here.
  # probably turn it into a function. 
  def compileReturn(self):
    #self.write_nonterm_begin("returnStatement")
    self.cadvance() #get 'return' keyword
    void_return = True
    while(self.nextIsTerm()):
      void_return = False
      self.compileExpression()
    if(void_return):
      self.vm_writer.writePush('constant',0)
    self.vm_writer.writeReturn() #this is the convention - return a constant 0 if void
    self.cadvance() #consume ;
    if(self.tok.current_token[1] != ";"):
      print('error: expected ; end of compileReturn')
    #self.write_nonterm_end()

  def nextIsTerm(self): #figures out if next token is a term
    #since expression := term (op term)* in the jack grammar, this basically defines isExpr too.
    nextType, nextVal = self.tok.lookAhead()
    #print("in nextIsTerm")
    #print("nextType, nextVal is "+nextType+" "+ nextVal)
    if(nextType in ["INT_CONST","STRING_CONST","IDENTIFIER"] or
      nextVal == "(" or nextVal in self.l_unary or nextVal in self.l_kwd_const):
      #( case covers '(' expression ')'
      #print("returning True")
      return True
    else:
      #print("returning False")
      return False

  def compileExpressionList(self): #modified to return a count to add to local var count in compileSubroutineCall
    #self.write_nonterm_begin("expressionList")
    count_for_locals = 0
    if(self.nextIsTerm()):
      self.compileExpression()
      count_for_locals += 1
    while(self.tok.lookAhead()[1] == ","):
      self.cadvance() #consume ,
      self.compileExpression()
      count_for_locals += 1
    return counter
    #self.write_nonterm_end()

  #I might be able to apply the compiler without expr or term to the expressionless syntax.  let's try.
  def compileExpression(self):
    #self.write_nonterm_begin("expression")
    self.compileTerm()
    '''
    while(next thing is binary operator):
      advance to get the operator
      compileTerm
    '''
    while(self.tok.lookAhead()[1] in self.l_binary):
      bop = self.cadvance()[1] #consume the binary op
      self.compileTerm()
      if(bop == "+"):
        self.vm_writer.writeArithmetic("add")
      elif(bop == "-"):
        self.vm_writer.writeArithmetic("sub")
      elif(bop == "*"):
        self.vm_writer.writeCall("Math.multiply", 2)
      elif(bop == "/"):
        self.vm_writer.writeCall("Math.divide", 2)
      elif(bop == "&"):
        self.vm_writer.writeArithmetic("and")
      elif(bop == "|"):
        self.vm_writer.writeArithmetic("or")
      elif(bop == "<"):
        self.vm_writer.writeArithmetic("lt")
      elif(bop == ">"):
        self.vm_writer.writeArithmetic("gt")
      elif(bop == "="):
        self.vm_writer.writeArithmetic("eq")
    #self.write_nonterm_end()

  def compileTerm(self):
    #self.write_nonterm_begin("term")

    isArray = False #track whether we get a [
    if(self.tok.lookAhead()[1] in self.l_unary):
      uop = self.cadvance()[1] #consume unary operator
      self.compileTerm() #recurse to term
      if(uop == "-"):
        self.vm_writer.writeArithmetic("neg") 
      elif(uop == "~"):
        self.vm_writer.writeArithmetic("not")

    elif(self.tok.lookAhead()[1] == '('): #parenthesized term
      self.cadvance()
      self.compileExpression()
      self.cadvance() #consume closing )
      if(self.tok.current_token[1] != ")"):
        print('error in compileTerm: expected ) to close term')

    elif(self.tok.lookAhead()[0] in ["INT_CONST"]): #have to separate int and string constants now!
      val = self.cadvance()[1] #consume integer val
      self.vm_writer.writePush('constant', val) #put it on the stack

    elif(self.tok.lookAhead()[0] in ["STRING_CONST"]): #have to separate int and string constants now!
      val = self.cadvance()[1] #consume string
      self.vm_writer.writePush('constant',len(val)) #this is the convention from the book, handling string const
      self.vm_writer.writeCall('String.new', 1)
      for vchar in val:
        self.vm_writer.writePush('constant', ord(vchar)) #ord gives the unicode int of the char
        self.vm_writer.writeCall('String.appendChar', 2) #the 2 arguments are the string itself and the char

    elif(self.tok.lookAhead()[1] in self.l_kwd_const): #literal term: true, false, null, this.
      val = self.cadvance()[1] #consume the literal/kwd constant
      if(val == "this"):
        self.vm_writer.writePush("pointer",0)
      else:
        self.vm_writer.writePush("constant",0) #null and false are encoded as 0 on the stack
        if(val == "true"):
          self.vm_writer.writeArithmetic("not") #puts "not 0" onto the stack (-1) which is encoded as True...

    elif(self.tok.lookAhead()[0] == "IDENTIFIER"):
      count_locals = 0  
      is_array = False
      iname = self.cadvance()[1] #consume identifier name
      nextVal = self.tok.lookAhead()[1] #have to lookahead here
      if(nextVal == '['): #array index expr
        is_array = True
        self.cadvance() #consume [
        self.compileExpression()
        self.cadvance() #consume ]
        self.compileArrayIndex(iname)
      if(nextVal == '.'): #is a subroutine call
        #update: after reviewing jack grammar, there are NO PUBLIC static or field vars!
        #so the only thing you can do with class instances is call their members.  can't access vars with .
        self.cadvance() #consume .
        sub_name = self.cadvance()[1] #consume subroutine name
        if((self.symbol_table.current_scope == "subroutine" and sub_name in self.symbol_table.subroutine_scope) or
           (sub_name in self.symbol_table.class_scope)):
          #if the name is in the current scope
          self.write_push(iname, sub_name) 
          iname = self.symbol_table.typeOf(iname) + "." + sub_name #case of variable: classname.method()
          count_locals += 1
        else:
          iname = iname + "." + sub_name #note: this is all identical to what's in compileDo
        
        self.cadvance() #consume (
        count_locals += self.compileExpressionList() 
        self.cadvance() #consume )
        self.vm_writer.writeCall(iname, count_locals)
      elif(nextVal == '('): #subroutine call
        count_locals += 1
        self.vm_writer.writePush('pointer', 0)
        self.cadvance() #consume (
        count_locals += self.compileExpressionList()
        self.cadvance() #consume )
        self.vm_writer.writeCall(self.class_name + "." + iname, count_locals)

      else:
        if(is_array): #this logic structure is ugly; we have 1 initial if, then an if-elif-else which depends on that if sequentially... might need to refactor this later.  it matters iff there are other terms after the array is hit somehow.
          self.vm_writer.writePop('pointer', 1)
          self.vm_writer.writePush('that', 0)
#the following section is begging to be refactored to be more pretty...
        elif((self.symbol_table.current_scope == "subroutine" and iname in self.symbol_table.subroutine_scope) or
           (iname in self.symbol_table.class_scope)):
          if(self.symbol_table.kindOf(iname) == "var"):
            self.vm_writer.writePush("local", self.symbol_table.indexOf(iname))
          elif(self.symbol_table.kindOf(iname) == "arg"):
            self.vm_writer.writePush("argument", self.symbol_table.indexOf(iname))
        else:
          if(self.symbol_table.kindOf(iname) == "static"):
            self.vm_writer.writePush("static", self.symbol_table.indexOf(iname))
          else:
            self.vm_writer.writePush("this", self.symbol_table.indexOf(iname))

      
    #self.write_nonterm_end()

  #should refactor the following - I think I might even have a repetition of the below logic somewhere above.  for now I leave it alone. It is very late.
  #LOOK INTO REMOVING subname FROM THIS: it is not used!!
  def write_push(self, name, subname): #dispatches push writes on kindOf
    #if name is in current scope:
    if((self.symbol_table.current_scope == "subroutine" and name in self.symbol_table.subroutine_scope) or
      (name in self.symbol_table.class_scope)):
      if(self.symbol_table.kindOf(name) == "var"):
        self.vm_writer.writePush("local", self.symbol_table.indexOf(name))
      elif(self.symbol_table.kindOf(name) == "arg"):
        self.vm_writer.writePush("argument", self.symbol_table.indexOf(name))
    else:
      if(self.symbol_table.kindOf(name) == "static"):
        self.vm_writer.writePush("static", self.symbol_table.indexOf(name))
      else:
        self.vm_writer.writePush("this", self.symbolTable.indexOf(name))

  def write_pop(self, name, subname): #dispatches pop writes on kindOf
    #if name is in current scope:
    if((self.symbol_table.current_scope == "subroutine" and name in self.symbol_table.subroutine_scope) or
      (name in self.symbol_table.class_scope)):
      if(self.symbol_table.kindOf(name) == "var"):
        self.vm_writer.writePop("local", self.symbol_table.indexOf(name))
      elif(self.symbol_table.kindOf(name) == "arg"):
        self.vm_writer.writePop("argument", self.symbol_table.indexOf(name))
    else:
      if(self.symbol_table.kindOf(name) == "static"):
        self.vm_writer.writePop("static", self.symbol_table.indexOf(name))
      else:
        self.vm_writer.writePop("this", self.symbolTable.indexOf(name))
