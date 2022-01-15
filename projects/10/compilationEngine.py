class CompilationEngine:

  l_decl_subroutine = ["constructor", "method", "function"]
  l_decl_classvar = ["static", "field"]

  def __init__(self, tokenizer, fout): #construct with an already-formed tokenizer, and an already opened file
    self.tok = tokenizer
    self.fout = fout

    self.element_stack = []
    self.indents = ""

  def write_nonterm_begin(self, element):
    self.fout.write(self.indents + "<" + element + ">\n")
    self.element_stack.append(element)
    self.increase_indents()
  def write_nonterm_end(self):
    element = self.element_stack.pop()
    self.decrease_indents()
    self.outputFile.write(self.indents + "</" + element + ">\n")
  def write_terminal(self):
    tokenType, tokenValue = tok.current_token #current_token is a type of tokentype, value
    tokenType = JackTokenizer.d_lex[tokenType] #get the XML form
    if(token[0] == "stringConstant"): #special case for string constant, annoying.
      tokenValue = tokenValue[1:-1] #get rid of the '"'
    self.fout.write(self.indents + "<" + tokenType + "> " + tokenValue + " </" + tokenType + ">\n")
 
  def increase_indents(self):
    self.indents += "  " 
  def decrease_indents(self):
    self.indents = self.indents[:-2]

  def cadvance(self): #a more convenient form of advance since we will write every advance
    self.tok.advance()
    self.write_terminal() #writes the current terminal token

  def compileClass(self):
    #this should be the first compile method called per compilation unit (file (one class per file)) 
    self.write_nonterm_begin("class")
    self.cadvance()
    if(self.tok.current_token[1] != "class"):
      print('error: expected "class" as first token in compileClass') #rudimentary error handling
    self.cadvance()
    if(self.tok.current_token[0] != "IDENTIFIER"):
      print('error: expected identifier after "class"')
    self.cadvance()
    if(self.tok.current_token[1] != "{"):
      print('error: expected {')
    
    while(self.tokenizer.hasMoreTokens() and (self.tok.lookAhead()[1] in l_decl_classvar)): #if next token begins class var declaration
      self.compileClassVarDec()
    while(self.tokenizer.hasMoreTokens() and (self.tok.lookAhead()[1] in l_decl_subroutine)): #if next token begins class var declaration
      self.compileSubroutine()

    self.cadvance()
    if(self.tok.current_token[1] != "}"):
      print('error: expected }')
    self.write_nonterm_end()
    self.fout.close() #we are done
   

  def compileClassVarDec(self):
    self.write_nonterm_begin("classVarDec")
    self.cadvance() #"static" or "field"
    if(self.tok.current_token[1] not in l_decl_classvar):
      print('error: expected "static" or "field"') #in retrospect this shouldn't be necessary since we only call this when this condition is satisfied.  could delete later.
    self.cadvance() #var type - we could add better error checking later.
    self.cadvance() #var name
    while(self.tok.lookAhead()[1] == ","):
      self.cadvance() # consume ','
      self.cadvance() # consume name
      if(self.tok.current_token[0] != "IDENTIFIER"):
        print('error: expected identifier (class variable name)')
      self.cadvance() # consume ";"
      if(self.tok.current_token[0] != ";"):
        print('error: expected ;')
    self.write_nonterm_end()

  def compileSubroutine(self):
    self.write_nonterm_begin("subroutineDec")
    self.cadvance() #consume  "constructor", "method", "function"
    self.cadvance() #consume type or 'void'
    self.cadvance() #consume subroutine name 
    self.cadvance() #consume (
    if(self.tok.current_token[0] != "("):
      print('error: expected (')
    self.compileParameterList()
    self.cadvance() #consume ) 
    self.compileSubroutineBody() #separate this out as a function for a bit of sanity
    self.write_nonterm_end()
      
  def compileParameterList(self):
    self.write_nonterm_begin("parameterList")
    while(self.tok.lookAhead()[1] != ")"):
      self.advance() #consume parameter type
      self.advance() #consume parameter name
      if(self.tok.lookAhead()[1] == ","):
        self.advance() #consume comma and loop around 
    self.write_nonterm_end() #note: we leave the ")" as the next token.  we did not consume it.

  def compileSubroutineBody(self):
    self.write_nonterm_begin("subroutineBody")
    self.advance() #consume {
    if(self.tok.current_token[1] != "{"):
      print('error: expected { for subroutine body')
    while(self.tok.lookAhead[1] == 'var'):
      self.compileVarDec()
    self.compileStatements()
    self.advance() #consume }
    if(self.tok.current_token[1] != "}"):
      print('error: expected } to end subroutine body')
    self.write_nonterm_end()

  def compileVarDec(self):
    pass
  
  def compileStatements(self):
    pass
