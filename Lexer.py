import re

class Lexer():

    def __init__(self, location):
      self.states = {0,1,2,3,4,5,6,7,8,9,10,11,12}
      self.finalStates = {3,4,7,9,12}
      self.initialState = 0
      self.currentState = self.initialState   
      self.symbols = {"+": "tkn_plus" ,"-": "tkn_minus" , "*": "tkn_times", "/": "tkn_div", "=": "tkn_equals", "<": "tkn_less", ">": "tkn_greater" , "<=": "tkn_leq" , ">=": "tkn_geq" , "<>": "tkn_diff", ".": "tkn_period", ",": "tkn_comma" , ":": "tkn_colon", "[": "tkn_left_brac" , "]": "tkn_right_brac", "()": "tkn_left_paren" , ")": "tkn_right_paren"}


      self.textLocation = location
      self.bufferedWord = ''      
      self.currentPosition = 0
      self.col = 0
      self.row = 1
      self.tokenBeginsRow = 0
      self.tokenBeginsCol = 0
      self.Tokens = []
    
    def reader(self):      
      with open(self.textLocation, 'r') as f:
        
        while True:

          char = f.read(1)          
          self.currentPosition += 1
          if not char:
              break          
          if char == '\n':
            self.row += 1
            self.col = 1
          else:
            self.col += 1          

          #command = input()
          '''
          if command == 'l':
            if self.currentPosition > 1:
              f.seek(self.currentPosition , 0)
              self.currentPosition -= 2
            else:
              f.seek(0,0)
              self.currentPosition = 0
          '''
          print( f"Caracter leído: {char}  Estado: {self.currentState}  Buffer: {self.bufferedWord} Posición: {self.currentPosition}")
          self.transition_state_func(char)
          
          f.seek(self.currentPosition,0)
      
      self.transition_state_func('EOF')
      for token in self.Tokens:
        print(token)
          
      
    def transition_state_func(self, char):  
      
      if char == 'EOF':
        self.Tokens.append(self.bufferedWord)

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
        elif re.search('[a-z]|[A-Z]|_', char):
          self.tokenBeginsRow = self.row      
          self.tokenBeginsCol = self.col
          self.bufferedWord +=  char
          self.currentState = 6
        
      
      elif self.currentState == 1:
        if char.isnumeric():
          self.bufferedWord += char
        elif char == '.':
          self.bufferedWord += char
          self.currentState = 5
        else:
          self.currentState = 4        

      elif self.currentState == 2:        
        if char in self.symbols:
          if (self.bufferedWord == "<" and (char == "=" or char== ">")) or (self.bufferedWord == ">" and char == "="):            
            self.bufferedWord += char     
            self.currentState = 3
          else:                    
            self.currentState = 3
        else:                    
          self.currentState = 3

      elif self.currentState == 3:   
        if len(self.bufferedWord) == 1:
          self.currentPosition -= 1    
        self.currentPosition -= 1       
        self.currentState = 0        
        self.Tokens.append(f"<{self.symbols[self.bufferedWord]}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
        self.bufferedWord = ""          

      elif self.currentState == 4:
        self.currentState = 0
        self.currentPosition -= 1
        self.Tokens.append(f"<tkn_number, {self.bufferedWord}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
        self.bufferedWord = ""

      
      elif self.currentState == 5:
        if char.isnumeric():
          self.bufferedWord += char
        else:
          self.currentState = 4          
      
      elif self.currentState == 6:
        if re.search('[a-z]|[A-Z]|_', char) != None or char.isnumeric():
          self.bufferedWord +=  char 
        else:
          self.currentState = 7
      
      elif self.currentState == 7:
        self.currentState = 0
        self.currentPosition -= 1
        self.Tokens.append(f"<id, {self.bufferedWord}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")
        self.bufferedWord = ""

      
          
      
      