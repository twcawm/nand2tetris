class JackTokenizer:

  l_keywords = {"class", "constructor", "function", "method", "field", "static", "var", 
              "int", "char", "boolean", "void", "true", "false", "null", "this",
              "let", "do", "if", "else", "while", "return"}
  l_symbols = {"{","}","(",")","[","]",".",",",";","+","-","*","/","&","|","<",">","=","-"}

  re_KEYWORD = '(?<!\w)('
  re_KEYWORD = re_KEYWORD + "|".join(l_keywords)
  re_KEYWORD = re_KEYWORD + ')(?!\w)'
  # '(?!\w)|' means "do not match \w (unicode word characters) after this".  \w means [a-zA-Z0-9_] basically.
  # and '(?<!\w)' does the same thing for "behind this".  basically, negative lookahead and lookbehind.
  '''
  re_SYMBOL 
  re_IDENTIFIER
  re_INT_CONST
  re_STRING_CONST
  '''

  def __init__(self, filename):
    f_jack = open(filename,'r')
    self.txt_jack = f_jack.read() #instead of readlines, we will use read() since comments can be multiline
    f_jack.close()
   
    self.remove_comments()



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
