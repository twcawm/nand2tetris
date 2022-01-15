import glob
import sys
import jackTokenizer
import compilationEngine

arg = sys.argv[1] #this could either be a .jack file or a directory containing .jack files

if(arg.endswith(".jack")):
  #it is a file
  tok = jackTokenizer.JackTokenizer(arg)
  filename_writer = arg[:-5]+".xml"
  fout = open(filename_writer,"w")
  compiler = compilationEngine.CompilationEngine(tok, fout)
  compiler.compileClass()
else:#assume it is a directory
  if(arg.endswith("/")):
    arg = arg[:-1] #chop off the directory /
  dn = arg.split("/")[-1] #the name of the final directory
  listfiles = glob.glob(arg+"/*.jack") #get list of all jack files to compile!
  print(listfiles)
  for infile in listfiles:
    tok = jackTokenizer.JackTokenizer(infile)
    filename_writer = infile[:-5]+".xml"
    fout = open(filename_writer,"w")
    compiler = compilationEngine.CompilationEngine(tok, fout)
    compiler.compileClass()
  
