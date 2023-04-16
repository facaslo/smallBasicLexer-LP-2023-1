import re
import sys

def isFloat(number):
  try:
    float(number)
    return True
  except ValueError:
    return False

class Lexer():

    def __init__(self, location):
      self.states = {0,1,2,3,4,5,6,7,8,9,10,11,12}
      self.finalStates = {3,4,7,9,12}
      self.initialState = 0
      self.currentState = self.initialState   
      self.symbols = {"+": "tkn_plus" ,"-": "tkn_minus" , "*": "tkn_times", "/": "tkn_div", "=": "tkn_equals", "<": "tkn_less", ">": "tkn_greater" , "<=": "tkn_leq" , ">=": "tkn_geq" , "<>": "tkn_diff", ".": "tkn_period", ",": "tkn_comma" , ":": "tkn_colon", "[": "tkn_left_brac" , "]": "tkn_right_brac", "(": "tkn_left_paren" , ")": "tkn_right_paren"}
      self.reservedWords = {'Stack','Program','Else', 'ElseIf', 'EndFor', 'EndIf', 'EndSub', 'EndWhile', 'For', 'Goto', 'If', 'Step', 'Sub', 'Then', 'To', 'While', 'And', 'Or', 'TextWindow', 'Array' }      

      self.inputList = sys.stdin
      self.inputText = "".join(self.inputList)

      self.textLocation = location
      self.bufferedWord = ''      
      self.currentPosition = 0
      self.col = 0
      self.row = 0
      self.comment = False
      self.lexError = False
      self.tokenBeginsRow = 0
      self.tokenBeginsCol = 0
      self.Output = {"tokens":[], "error": ""}
    
    def readFile(self):          
      self.row = 1  
      with open(self.textLocation, 'r' , encoding='utf-8') as f:
        visitedLineEnds = set({})
        while True:          
          char = f.read(1)          
          self.currentPosition += 1
          if not char:
            break          
          if char == "'":
            self.comment = True
          elif char == '\n':
            if not(self.currentPosition in visitedLineEnds):              
              visitedLineEnds.add(self.currentPosition)  
              self.row += 1          
            self.col = 0 
            self.comment = False
          else:
            self.col += 1          
            if not self.comment:
              self.transition_state_func(char)                   
          # Update pointer position
          f.seek(self.currentPosition,0)      
      self.transition_state_func('EOF') 

    def readStream(self):
      for line in self.inputList:
        '''
        if 'Exit' == line.rstrip():           
          break
        '''
        self.comment = False
        self.row += 1
        self.col = 1
        while self.col <= len(line) and self.lexError == False:
          char = line[self.col-1]          
          #print(line[self.col-1] , end = "")
          if not self.comment: 
            #print(f"char_a:{line[self.col-1]} - state_a:{self.currentState} - buffer_a:{self.bufferedWord} - row_a:{self.row} - col_a:{self.col}")
            self.transition_state_func(char)            
          if (not self.comment) and char == "'" and not(self.currentState==8 or self.currentState==9 ):
            self.comment = True
          #print(f"char_b:{line[self.col-1]} - state_b:{self.currentState} - buffer_b:{self.bufferedWord} - row_b:{self.row} - col_b:{self.col}")                
          self.col += 1          
      self.transition_state_func('EOF')

    def readNextToken(self):
      text = self.inputText
      for position in range(self.currentPosition,len(text)):        
        #print(text[position].encode() , position)
        self.currentPosition += 1
      
    def transition_state_func(self, char):
      
      if (not(char in self.symbols.keys() or re.search('[À-ž]|[A-Z]|[a-z]|ñ|ç|_|[^\x00-\x7F]', char) != None or char.isnumeric() or char in set({"\r", "\n" , "\t" , " ", "'", "\""})) and not(self.currentState == 8 or self.currentState == 9)) or (char=="_" and self.currentState==0):                    
          self.Output['error'] = f">>> Error lexico (Linea: {self.row}, Posicion: {self.col})"
          self.lexError = True
          return
      
      elif (char == 'EOF' or self.lexError) and self.bufferedWord != "":         
      
        if self.currentState == 2 or self.currentState == 3:          
          self.Output["tokens"].append(f"<{self.symbols[self.bufferedWord]}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")

        if self.currentState == 1 or self.currentState == 5:
          if self.bufferedWord.isnumeric() or isFloat(self.bufferedWord):
            self.Output["tokens"].append(f"<tkn_number, {self.bufferedWord}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
          else:
            self.Output["tokens"].append(f"<tkn_number, {self.bufferedWord[0:len(self.bufferedWord)-1]}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
            self.Output["tokens"].append(f"<tkn_period, {self.row}, {self.col - 1}>")

        elif self.currentState == 6:
          if self.bufferedWord in self.reservedWords:
            self.Output["tokens"].append(f"<{self.bufferedWord}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
          else:
            self.Output["tokens"].append(f"<id, {self.bufferedWord}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")

        elif self.currentState == 8:
          if self.bufferedWord[-1] != "\"":
            self.Output['error'] = f">>> Error lexico (Linea: {self.tokenBeginsRow}, Posicion: {self.tokenBeginsCol})"
            self.lexError = True
            return

        elif self.currentState == 9:
          if self.bufferedWord.lower() == "true":
           self.Output["tokens"].append(f"<True, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
          elif self.bufferedWord.lower() == "false":
            self.Output["tokens"].append(f"<False, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")          
          else:
            self.Output["tokens"].append(f"<tkn_text, {self.bufferedWord}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")

      elif self.currentState == 0:                
        if char in self.symbols.keys():    
          self.tokenBeginsRow = self.row      
          self.tokenBeginsCol = self.col
          self.bufferedWord += char
          self.currentState = 2          
        elif char.isnumeric():
          self.tokenBeginsRow = self.row      
          self.tokenBeginsCol = self.col
          self.bufferedWord += char
          self.currentState = 1
        elif re.search('[À-ž]|[A-Z]|[a-z]|ñ|ç|[^\x00-\x7F]', char):
          self.tokenBeginsRow = self.row      
          self.tokenBeginsCol = self.col
          self.bufferedWord +=  char
          self.currentState = 6
        elif char == "\"":      
          self.tokenBeginsRow = self.row      
          self.tokenBeginsCol = self.col    
          self.currentState = 8       
              
      elif self.currentState == 1:
        if char.isnumeric():
          self.bufferedWord += char
        elif char == '.':
          self.bufferedWord += char
          self.currentState = 5
        else:
          self.col -= 1
          self.currentPosition -= 1
          self.currentState = 4        

      elif self.currentState == 2:        
        if (self.bufferedWord == "<" and (char == "=" or char== ">")) or (self.bufferedWord == ">" and char == "="):            
          self.bufferedWord += char
          self.currentState = 3

        else:
          self.currentPosition -= 1 
          self.col -= 1   
          self.Output["tokens"].append(f"<{self.symbols[self.bufferedWord]}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
          self.bufferedWord = ""
          self.currentState = 0            
          
      elif self.currentState == 3:           
        self.currentPosition -= 1       
        self.col -= 1   
        self.currentState = 0        
        self.Output["tokens"].append(f"<{self.symbols[self.bufferedWord]}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
        self.bufferedWord = ""                            

      elif self.currentState == 4:
        self.currentState = 0
        self.currentPosition -= 1
        self.col -= 1           
        if self.bufferedWord.isnumeric() or isFloat(self.bufferedWord):
          self.Output["tokens"].append(f"<tkn_number, {self.bufferedWord}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
        else:
          self.Output["tokens"].append(f"<tkn_number, {self.bufferedWord[0:len(self.bufferedWord)-1]}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
          self.Output["tokens"].append(f"<tkn_period, {self.row}, {self.col}>")
        self.bufferedWord = ""
      
      elif self.currentState == 5:
        if char.isnumeric():
          self.bufferedWord += char
        else:
          self.currentPosition -= 1
          self.col -= 1
          self.currentState = 4         
      
      elif self.currentState == 6:
        if re.search('[À-ž]|[A-Z]|[a-z]|ñ|ç|_|[^\x00-\x7F]', char) != None or char.isnumeric():
          self.bufferedWord +=  char 
        else:
          self.currentPosition -= 1
          self.col -= 1
          self.currentState = 7
      
      elif self.currentState == 7:
        self.currentState = 0
        self.currentPosition -= 1
        self.col -= 1   
        if self.bufferedWord in self.reservedWords:
          self.Output["tokens"].append(f"<{self.bufferedWord}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
        else:
          self.Output["tokens"].append(f"<id, {self.bufferedWord}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
        self.bufferedWord = ""

      elif self.currentState == 8:
        if char not in {"\"", "\n"}:         
          self.bufferedWord += char          
        elif char == "\"":          
          self.currentState = 9

      elif self.currentState == 9:
        self.currentState = 0
        self.currentPosition -= 1
        self.col -= 1         
        if self.bufferedWord.lower() == "true":
          self.Output["tokens"].append(f"<True, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
        elif self.bufferedWord.lower() == "false":
          self.Output["tokens"].append(f"<False, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
        else:
          self.Output["tokens"].append(f"<tkn_text, {self.bufferedWord}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
        self.bufferedWord = "" 

    def printTokens(self):   
      
      for i in range(len(self.Output["tokens"])-1):
        print(self.Output["tokens"][i])
      if len(self.Output["tokens"]) > 0:
        print(self.Output["tokens"][len(self.Output["tokens"])-1],end="")
      
      if self.Output["error"] != "":
        print(f"\n{self.Output['error']}")