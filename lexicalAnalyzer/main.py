from lexer import Lexer

if __name__ == "__main__":
    l = Lexer("")
    while(True):      
      token = l.readNextToken()
      if token == None:
          break        
      print(token)

    lexError = l.returnLexError()
    if lexError != None:
        print(lexError)