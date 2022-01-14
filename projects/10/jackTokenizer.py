import re

class JackTokenizer:

  l_keywords = ["class", "constructor", "function", "method", "field", "static", "var", 
              "int", "char", "boolean", "void", "true", "false", "null", "this",
              "let", "do", "if", "else", "while", "return"]
  l_symbols = ["{","}","(",")","[","]",".",",",";","+","-","*","/","&","|","<",">","=","-"]
  d_lex = {"KEYWORD":"keyword",
           "SYMBOL":"symbol",
           "IDENTIFIER":"identifier",
           "INT_CONST":"integerConstant",
           "STRING_CONST":"stringConstant"}

  re_KEYWORD = '(?<!\w)' + '(?!\w)|(?<!\w)'.join(l_keywords)+'(?!\w)'
  # '(?!\w)|' means "do not match \w (unicode word characters) after this".  \w means [a-zA-Z0-9_] basically.
  # and '(?<!\w)' does the same thing for "behind this".  basically, negative lookahead and lookbehind.
  # note: doing this with '(?<!\w)(class|constructor|...)(?!\w)' DID NOT WORK when combined with other regex,
  #   but worked on its own.  pretty confusing.
  re_SYMBOL = "[" + re.escape("|".join(l_symbols)) + "]" #re.escape ensures the characters like { or . (characters with special meaning in regex) are escaped to mean literally those characters
  re_IDENTIFIER = r"[\w]+" #+ means "at least 1".  \w means word character.  [] means a set.  I'm not 100% sure if the [] is needed here, but this works.
  re_INT_CONST = r"[0-9]+" # similar to re_IDENT.  \d matches things like... Eastern Arabic etc.
  re_STRING_CONST = r'"[^"\n]*"' #starts with ".  [^...] denotes COMPLEMENT of a group. so match any number of anything except newlines and other ", then end with ".  

  #re_lex_element = "|".join([re_KEYWORD,re_SYMBOL,re_IDENTIFIER,re_INT_CONST,re_STRING_CONST])
  re_lex_element = "|".join([re_KEYWORD,re_SYMBOL,re_INT_CONST,re_STRING_CONST,re_IDENTIFIER])
  #print("re_lex_element: " + re_lex_element)
  compiled_lex_element = re.compile(re_lex_element) #this is an attempt to match all lexical elements of the Jack language

  def __init__(self, filename):
    f_jack = open(filename,'r')
    self.txt_jack = f_jack.read() #instead of readlines, we will use read() since comments can be multiline
    f_jack.close()
   
    self.remove_comments()
    self.all_lex_elements = self.compiled_lex_element.findall(self.txt_jack) #list of all lexical elements
    self.tokens = self.make_token_list(self.all_lex_elements) #list of tuples of lexelement type, value (lexement)
 
    self.current_index = -1 #we need to all advance() to get to the first element of the tokens list.
    self.current_token = None

    self.fix_symbols()
    #self.output_xml()


  def output_xml(self):
    print("<tokens>") 
    for token in self.tokens:
      print("<"+self.d_lex[token[0]]+"> "+token[1]+" </"+self.d_lex[token[0]]+">")
    print("</tokens>") 
      
  def fix_symbols(self):
    #replace <, >, ", &
    replacers = {'<': '&lt;', 
                 '>': '&gt;',
                 '"': '&quot;',
                 '&': '&amp;' 
                }
    new_tokens = []
    for token in self.tokens:
      if(token[0] == "SYMBOL" and token[1] in replacers):
        new_tokens.append((token[0], replacers[token[1]]))
      else:
        new_tokens.append((token[0],token[1]))
    self.tokens = new_tokens

  def hasMoreTokens(self):
    return self.current_index < (len(self.tokens) - 1)

  def advance(self):
    if(not hasMoreTokens):
      print("error: advance() called without any more tokens left")
    else:
      self.current_index = self.current_index + 1
      self.current_token = self.tokens[self.current_index]

  def tokenType(self): #returns which type of lexical element it is
    return self.current_token[0] #we already set up self.tokens to store this info

  def keyWord(self): #returns which keyword it is
    if(self.tokenType() == "KEYWORD"):
      return self.current_token[1] #essentially already stored
    else:
      print("error: keyWord() called when tokenType() is not KEYWORD")

  def symbol(self):
    if(self.tokenType() == "SYMBOL"):
      return self.current_token[1]
    else:
      print("error: symbol() called when tokenType() is not SYMBOL")

  def identifier(self): 
    if(self.tokenType() == "IDENTIFIER"):
      return self.current_token[1]
    else:
      print("error: identifier() called when tokenType() is not IDENTIFIER")

  def intVal(self): 
    if(self.tokenType() == "INT_CONST"):
      return int(self.current_token[1])
    else:
      print("error: intVal() called when tokenType() is not INT_CONST")

  def stringVal(self):
    if(self.tokenType() == "STRING_CONST"):
      return int(self.current_token[1])
    else:
      print("error: stringVal() called when tokenType() is not STRING_CONST")

  def make_token_list(self, l_lex_elements):
    return [(self.lex2token(lex_element), lex_element) for lex_element in l_lex_elements]

  def lex2token(self, lex_element): #lex_element: one element of the list returned by findall on compiled_lex_element
    if(re.match(self.re_KEYWORD, lex_element) ):
      return "KEYWORD"
    elif(re.match(self.re_SYMBOL, lex_element) ):
      return "SYMBOL"
    elif(re.match(self.re_INT_CONST, lex_element) ):
      return "INT_CONST"
    elif(re.match(self.re_STRING_CONST, lex_element) ):
      return "STRING_CONST"
    elif(re.match(self.re_IDENTIFIER, lex_element) ):
      return "IDENTIFIER"
    else:
      print("error in lex2token in lexer: lexical element not recognized")

  
   
    

  def remove_comments(self):
    #parse through the entire self.txt_jack
    #  when we encounter a string literal, just get through it and ignore anything in it
    #  else, when not in a string literal, watch for /* and //
    #    if /*, erase anything until the nearest */ (can be on a separate line)
    #      then continue immediately after the */
    #    if //, just find the nearest newline and continue immediately after that
    i = 0 # i is just going to be the index in the string
    end = 0 # end will be used to keep track of where the end of strings and comments are
    i_eof = len(self.txt_jack) # this is 1 greater than the limit for indexing self.txt_jack
    txt_rm = '' #this will store the txt with removed comments

    
    #note: the detection of string literals we use here is possible bc Jack specifies that
    #  string literals do not contain newlines.
    #  we're basically using a finite stat machine that starts in "not a string" and enters
    #    "in string" when it encounters a first instance of '"'.
    #  also, I believe there are no escape characters for placing something like \" in a Jack string
    #  which also makes it easier.  we can just find the first instance of any " after we're in a string.
    while(i < i_eof):
      if(self.txt_jack[i] == '"'): 
        end = self.txt_jack.find('"', i+1)
        txt_rm = txt_rm + self.txt_jack[i:end+1] #keep the string literal
        i = end + 1 #put cursor 1 past end of that string
      elif(self.txt_jack[i] == '/'):
        if(self.txt_jack[i+1] == '/'): #is a 1-line comment - find the next newline
          end = self.txt_jack.find('\n', i+2) #start 2 past current index since we have //
          i = end + 1 #put cursor 1 past end of the comment (next line basically)
          txt_rm = txt_rm + " " #add just a space in place of the comment
        elif(self.txt_jack[i+1] == '*'):
          end = self.txt_jack.find('*/', i+2) #start 2 past current index since we have //
          i = end + 2 #since end points to * in */, we want 1 past /, which is 2 past *
          txt_rm = txt_rm + " " #add just a space in place of the comment
        else: #else it's just literally a /, so keep it
          txt_rm = txt_rm + self.txt_jack[i]
          i = i + 1
      else: #we're not in a string or a comment.  so just append the current character
        txt_rm = txt_rm + self.txt_jack[i]
        i = i + 1
    self.txt_jack = txt_rm #set the self.txt_jack to the version with comments removed. 
    return
