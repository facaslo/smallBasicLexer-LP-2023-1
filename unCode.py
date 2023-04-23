import re
import sys

def isFloat(number):
  try:
    float(number)
    return True
  except ValueError:
    return False

class Lexer():
########################################################################################################
    #def __init__(self, location):
    def __init__(self, inputList):
      self.states = {0,1,2,3,4,5,6,7,8,9,10,11,12}
      self.finalStates = {3,4,7,9,12}
      self.initialState = 0
      self.currentState = self.initialState   
      self.symbols = {"+": "tkn_plus" ,"-": "tkn_minus" , "*": "tkn_times", "/": "tkn_div", "=": "tkn_equals", "<": "tkn_less", ">": "tkn_greater" , "<=": "tkn_leq" , ">=": "tkn_geq" , "<>": "tkn_diff", ".": "tkn_period", ",": "tkn_comma" , ":": "tkn_colon", "[": "tkn_left_brac" , "]": "tkn_right_brac", "(": "tkn_left_paren" , ")": "tkn_right_paren"}
      self.reservedWords = {'Stack','Program','Else', 'ElseIf', 'EndFor', 'EndIf', 'EndSub', 'EndWhile', 'For', 'Goto', 'If', 'Step', 'Sub', 'Then', 'To', 'While', 'And', 'Or', 'TextWindow', 'Array' }      

      self.inputList = inputList
      copyOfList = self.inputList.copy()
      self.inputText = "".join(copyOfList).replace("\r", "")

      #self.textLocation = location
      self.bufferedWord = ''      
      self.currentPosition = 0      
      self.col = 0
      self.row = 1
      self.comment = False
      self.lexError = False
      self.tokenBeginsRow = 0
      self.tokenBeginsCol = 0
      self.Output = {"tokens":[], "error": ""}
      self.visitedLineEnds = set({})

########################################################################################################    
    def readStream(self):
      self.row = 0
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
########################################################################################################
    def readNextToken(self):

      text = self.inputText
      tokenList = self.Output["tokens"]      
      lastToken =  tokenList[-1] if len(tokenList) > 0 else None    

      while self.currentPosition < len(text) and self.lexError == False:
        
        originalPosition = self.currentPosition
        currentLastToken =  tokenList[-1] if len(tokenList) > 0 else None 
        if currentLastToken != lastToken:
          return currentLastToken

        currentCharacter = text[self.currentPosition]                
        self.col += 1

        if (not self.comment) and currentCharacter == "'" and not(self.currentState==8 or self.currentState==9 ):
          self.comment = True                            

        else:       
          if not self.comment:
            self.transition_state_func(currentCharacter) 
        
        if currentCharacter == "\n":  
          if originalPosition not in self.visitedLineEnds:                                       
                  
            self.visitedLineEnds.add(originalPosition)  
            self.row += 1

          self.col = 0
          self.comment  = False       
                  
          
        self.currentPosition += 1
        
      if self.currentPosition == len(text) or self.lexError:
        self.transition_state_func('EOF') 
        currentLastToken =  tokenList[-1] if len(tokenList) > 0 else None   
        if currentLastToken != lastToken and currentLastToken != None:              
          return currentLastToken
      
      return None
########################################################################################################    
    def returnLexError(self):
      if self.lexError:
        return self.Output["error"]
      return None
########################################################################################################
    def printText(self):
      for char in self.inputText:
        print(char.encode())

########################################################################################################
    def transition_state_func(self, char):
      
      if (not(char in self.symbols.keys() or re.search('[À-ž]|[A-Z]|[a-z]|ñ|ç|_|[^\x00-\x7F]', char) != None or char.isnumeric() or char in set({"\r", "\n" , "\t" , " ", "'", "\""})) and not(self.currentState == 8 or self.currentState == 9)) or (char=="_" and self.currentState==0):                    
          self.Output['error'] = f">>> Error lexico (Linea: {self.row}, Posicion: {self.col})"
          self.lexError = True
          return
      
      elif (char == 'EOF' or self.lexError):
        if (self.bufferedWord != ""):
          if self.currentState == 2 or self.currentState == 3:          
            self.Output["tokens"].append(f"<{self.symbols[self.bufferedWord]}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")

          if self.currentState == 1 or self.currentState == 5:
            if self.bufferedWord.isnumeric() or isFloat(self.bufferedWord):
              self.Output["tokens"].append(f"<tkn_number, {self.bufferedWord}, {self.tokenBeginsRow}, {self.tokenBeginsCol}>")        

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


numberIter = 10000

def readInput(grammarInputString):            
    grammarInputList =  grammarInputString.split("\n")    

    terminal_symbols = set(grammarInputList[0].strip().split(','))   

    # Read the second line of input and split it into its non-terminal symbols
    non_terminal_symbols = set(grammarInputList[1].strip().split(','))

    # Read the third line of input and split it into its grammar rules
    grammar_rules = grammarInputList[2].strip().split(',')

    starting_symbol = grammarInputList[3].strip()

    # Read the fourth line of input and split it into its operators
    # operators = input().strip().split(',')

    # Create an empty dictionary to store the grammar rules
    grammar_dict = {}

    # Loop through each grammar rule
    for rule in grammar_rules:
        # Split the rule into its non-terminal symbol and its right-hand side
        non_terminal_symbol, right_hand_side = rule.strip().split(' -> ')

        # Split the right-hand side into its individual options
        options = right_hand_side.split('|')

        # Add the options to the dictionary
        grammar_dict[non_terminal_symbol] = [option.strip().split(' ') for option in options]        

    return terminal_symbols, non_terminal_symbols, grammar_dict , starting_symbol

def printGrammar(grammar):
  print("Simbolos terminales: ", grammar[0] )
  print("Simbolos no terminales: ", grammar[1] )
  for nonTerminal in grammar[2]:
     derivationList = []
     for derivation in grammar[2][nonTerminal]:
        derivationAsString = " ".join(derivation)
        derivationList.append(derivationAsString)

     print (str(nonTerminal) + " -> " +  " | ".join(derivationList))

def compute_firsts_sets(terminal_symbols, non_terminal_symbols, grammar_dict):
  
    # Initialize an empty dictionary to store the FIRST sets
    first_sets = {}

    # Initialize the FIRST sets for all terminal symbols
    for symbol in terminal_symbols:        
        first_sets[symbol] = {symbol}

    # Initialize the FIRST sets for all non-terminal symbols to the empty set
    for symbol in non_terminal_symbols:
        first_sets[symbol] = set({})

    # Find the first elements that are terminals
    for nonTerminal , rules in grammar_dict.items():
      for rule in rules:
        firstSymbol = rule[0] 
        if firstSymbol in terminal_symbols and firstSymbol not in first_sets[nonTerminal]:
            first_sets[nonTerminal].add(firstSymbol)
            

    # Find the first elements that are not terminals
    counter = 0
    while counter < numberIter:

      
      for nonTerminal , rules in grammar_dict.items():
        for rule in rules:
          firstSymbol = rule[0] 

          if firstSymbol in non_terminal_symbols:
            derivation_first_set = set({})
            hasEpsilon = True                   

            for symbol in rule:
              if len(first_sets[symbol]) > 0:       
                derivation_first_set |= first_sets[symbol] - {"epsilon"}      
                if ("epsilon" not in first_sets[symbol]):
                  hasEpsilon = False
                  break      
                                      
            if len(derivation_first_set) > 0 and not (derivation_first_set-{"epsilon"}).issubset(first_sets[nonTerminal]):
              first_sets[nonTerminal] |= derivation_first_set - {"epsilon"}
              
              if (hasEpsilon):
                first_sets[nonTerminal] |= {"epsilon"}    
      counter += 1

    return first_sets

def compute_rule_first_set(first_sets, terminal_symbols, non_terminal_symbols, input_string):
  string_firsts_sets = set({})
  if input_string.strip() == "epsilon":
    return {"epsilon"}
  
  input_string = input_string.strip().split(" ")
  input_string = [input_string_element.strip() for input_string_element in  input_string]
  first_symbol = input_string[0]
  
  if input_string[0] in terminal_symbols:
    return {first_symbol}
  elif input_string[0] in non_terminal_symbols:
    string_firsts_sets |= (first_sets[first_symbol]-{"epsilon"})
  if "epsilon" in first_sets[first_symbol]:
    if len(input_string) == 1:
      string_firsts_sets.add("epsilon")      
    else:
      string_firsts_sets |= compute_rule_first_set(first_sets, terminal_symbols, non_terminal_symbols, " ".join(input_string[1:]))
  return string_firsts_sets 

def compute_rules_firsts(first_sets, terminal_symbols, non_terminal_symbols, grammar_dict):
  rules_firsts = {}
  for nonTerminal, rules in grammar_dict.items():
    for rule in rules:
      ruleString = " ".join(rule)
      rules_firsts_set = compute_rule_first_set(first_sets, terminal_symbols, non_terminal_symbols, ruleString)
      ruleKey = nonTerminal + " -> " + ruleString
      rules_firsts[ruleKey] = rules_firsts_set
  return rules_firsts

def compute_follows_sets( first_sets, terminal_symbols, non_terminal_symbols, grammar_dict, startingSymbol):
  followingSets = {}
  
  # Initialize the FIRST sets for all non-terminal symbols to the empty set
  for symbol in non_terminal_symbols:
      followingSets[symbol] = set({})
  
  followingSets[startingSymbol] |= {"$"}

  
  
  counter = 0
  while counter < numberIter:    
    
    
    for nonTerminal in non_terminal_symbols:
      for leftHandSymbol , rules in grammar_dict.items():
        for rule in rules:
          for i in range(len(rule)):
            if rule[i] == nonTerminal:
              beta = " ".join(rule[i+1:len(rule)]) if i < len(rule)-1 else "epsilon"
              toAdd = compute_rule_first_set(first_sets, terminal_symbols, non_terminal_symbols, beta) 
              if (not((toAdd - {"epsilon"}).issubset(followingSets[nonTerminal])) and len(toAdd)>0):
                
                followingSets[nonTerminal] |= (toAdd - {"epsilon"})
              if "epsilon" in toAdd or beta=="epsilon":                
                followingSets[nonTerminal] |= followingSets[leftHandSymbol]
    
    counter += 1
  return followingSets
  

def compute_rule_prediction_set(rules_firsts_set,follows_sets, rule):
  leftHandSymbol = rule.strip().split(" -> ")[0].strip()  
  if "epsilon" in rules_firsts_set[rule]:
    return (rules_firsts_set[rule] - {"epsilon"}) | follows_sets[leftHandSymbol]
  else:
    return rules_firsts_set[rule]
  
def compute_rules_predictions(compute_rules_firsts_set,compute_follows_sets,grammar_dict):
  rules_predictions_set = {}
  for nonTerminal, rules in grammar_dict.items():
    for rule in rules:
      ruleString = nonTerminal + " -> " + " ".join(rule)
      predictionSet = compute_rule_prediction_set(compute_rules_firsts_set,compute_follows_sets,ruleString)
      rules_predictions_set[ruleString] = predictionSet
  return rules_predictions_set

def isLL1(predictionsSet):  
  predictionsSetCopy = predictionsSet.copy()
  elements = [[key.strip().split("->")[0].strip(), value.copy()]  for key, value in predictionsSetCopy.items()]
  joinedSets = {}
  ll1 = True
  elementsCopy = elements.copy()
  for i in range(len(elementsCopy)):    
    nonTerminal = elementsCopy[i][0]
    currentPredictionSet = elementsCopy[i][1]
    if not (nonTerminal in joinedSets.keys()):
      joinedSets[nonTerminal] = currentPredictionSet
    elif joinedSets[nonTerminal].intersection(currentPredictionSet):
      ll1 = False
      break
    else:
      joinedSets[nonTerminal] |= currentPredictionSet  
  return ll1 

def returnInfo(grammarInputString):  
  readed = readInput(grammarInputString)  
  terminal_symbols = readed[0] 
  non_terminal_symbols = readed[1]
  grammar_dict = readed[2]
  startingSymbol = readed[3]
  first_sets = compute_firsts_sets(terminal_symbols,non_terminal_symbols, grammar_dict)
  follows_sets = compute_follows_sets(first_sets, terminal_symbols,non_terminal_symbols,grammar_dict, startingSymbol)
  rules_firsts = compute_rules_firsts(first_sets,terminal_symbols,non_terminal_symbols,grammar_dict)
  predictions = compute_rules_predictions(rules_firsts,follows_sets,grammar_dict)  
  isLL1Grammar = isLL1(predictions.copy())   
  info = { 
    "Terminal symbols" : terminal_symbols ,
    "Non terminal symbols" : non_terminal_symbols,
    "Starting symbol": startingSymbol,
    "Grammar" : grammar_dict,
    "First sets" : first_sets,
    "Follows sets" : follows_sets,
    "Rules firsts sets" : rules_firsts,
    "Prediction sets" : predictions,
    "Is LL1" : isLL1Grammar
  }  
  return info

def printGrammarSets(grammarInputString):
  readed = readInput(grammarInputString)
  print()
  print("Grammar")
  printGrammar(readed)
  print()

  terminal_symbols = readed[0] 
  non_terminal_symbols = readed[1]
  grammar_dict = readed[2]
  startingSymbol = readed[3]


  print("firsts")
  first_sets = compute_firsts_sets(terminal_symbols,non_terminal_symbols, grammar_dict)
  for key in grammar_dict:
    print(key , first_sets[key])
  print()

  print("Follows")
  follows_sets = compute_follows_sets(first_sets, terminal_symbols,non_terminal_symbols,grammar_dict, startingSymbol)
  for key in grammar_dict:
    print(key , follows_sets[key])
  print()

  print("rules_firsts")
  rules_firsts = compute_rules_firsts(first_sets,terminal_symbols,non_terminal_symbols,grammar_dict)
  for key, value in rules_firsts.items():
    print(key , value)
  print()

  print("predictions")
  predictions = compute_rules_predictions(rules_firsts,follows_sets,grammar_dict)
  for key, value in predictions.items():
    print(key , value)
  print()

  print(isLL1(predictions))
 
###############################################################################################
def storeConsoleInput():
  return list(sys.stdin)

class syntaxAnalizer():    
  def __init__(self):
    self.consoleInput = storeConsoleInput()
    self.lex = Lexer(self.consoleInput)
    self.grammarString = '''tkn_plus,tkn_minus,tkn_times,tkn_div,tkn_equals,tkn_less,tkn_greater,tkn_leq,tkn_geq,tkn_diff,tkn_period,tkn_comma,tkn_colon,tkn_left_brac,tkn_right_brac,tkn_left_paren,tkn_right_paren,Stack,Program,Else,ElseIf,EndFor,EndIf,EndSub,EndWhile,For,Goto,If,Step,Sub,Then,To,While,And,Or,TextWindow,Array,True,False,tkn_number,tkn_text,id,epsilon
Assign,AssignP,Expr,RestExpr,Term,RestTerm,Factor,LExpr,RestLExpr,lValue,CValue,CValueP,RestCvalue,RestCValue2,LVariable,LDigit,TruthValue,RestFactor,TextValue,TExpr,RestTExpr,TValue
Assign -> id tkn_equals TExpr Assign | epsilon,TExpr -> TValue RestTExpr ,RestTExpr -> tkn_plus TValue RestTExpr  | epsilon,TValue -> TextValue | LExpr,LExpr ->  lValue RestLExpr,RestLExpr -> Or lValue RestLExpr | And lValue RestLExpr | epsilon,lValue -> TruthValue | CValue ,CValue -> Expr RestCvalue,RestCvalue -> tkn_less Expr | tkn_leq Expr  | tkn_greater Expr | tkn_geq Expr | tkn_diff Expr | epsilon, Expr -> Term RestExpr,RestExpr -> tkn_minus Term RestExpr | epsilon , Term -> Factor RestTerm , RestTerm -> tkn_times Factor RestTerm | tkn_div Factor RestTerm | epsilon , Factor -> tkn_minus RestFactor | RestFactor,RestFactor -> tkn_number | id | tkn_left_paren TExpr tkn_right_paren,TruthValue -> True | False ,TextValue -> tkn_text
Assign
''' 
        
    self.grammar = returnInfo(self.grammarString)        
    #print( self.grammar["Prediction sets"]  )
    #print()
    grammarSet = []
    for key, value in self.grammar["Grammar"].items():        
        for i in range(len(value)):
          output = key + " -> " + " ".join(value[i])          
          grammarSet.append(output)
    
    self.grammar["Grammar"] = grammarSet    

    self.rules = self.grammar["Grammar"]
    self.predictionSets = self.grammar["Prediction sets"]    
    self.readNextToken()    
    self.syntaxError = False
    self.lastRule = None
    self.MultilineSentence = False
    
    #print(self.grammar["Is LL1"])
    #print(self.predictionSets)

  def readNextToken(self):
    nextToken = self.lex.readNextToken()
    if nextToken != None:
      self.token = self.parseTokenInfo(nextToken) 
    else:
      self.token = {"type" : "$" , "row": self.lex.row , "col": self.lex.col + 1}    

  def nonTerminal(self , nonTerminalSymbol):    
   if not(self.syntaxError):
    predictionsForNT = self.getPredictionsForNT(nonTerminalSymbol)   
    tokenInPredictionSet = False
    for rule,predictionSet in predictionsForNT.items():            
      if self.token["type"] in predictionSet and tokenInPredictionSet==False:
        tokenInPredictionSet = True
        self.lastRule  = (rule ," ---- " ,self.token, " ---- " , self.predictionSets[rule])
        print(rule ," ---- " ,self.token, " ---- " , self.predictionSets[rule])
        ruleSymbolsList = []
        for symbol in rule.split("->")[1:][0].strip().split(" "):
          ruleSymbolsList.append(symbol)
        #ruleSymbolsList = [symbol.strip() for symbol in rule.split("->")[1:][0].strip().split(" ")]
        #if not(ruleSymbolsList == ["epsilon"]):
        for ruleSymbol in ruleSymbolsList:          
          if ruleSymbol in self.grammar["Terminal symbols"]:          
            #print("Terminal:", symbol)          
            self.pairing(ruleSymbol)
          elif ruleSymbol in self.grammar["Non terminal symbols"]:
            #print("Non terminal:", symbol)
            self.nonTerminal(ruleSymbol)
              
          
    
    if not(tokenInPredictionSet): 
      self.syntaxError = True
      if self.token["type"] != "$":      
        print(f"Error sintáctico en row: {self.token['row']} col: {self.token['col']}, se esperaba {[j for i in list(predictionsForNT.values()) for j in i]} , se encontró {self.token['type']}")          
        print(self.lastRule)  
      else:
        print(f"Error sintáctico en en row: {self.token['row']} col: {self.token['col']}, se esperaba {[j for i in list(predictionsForNT.values()) for j in i]} , se encontró {self.token['type']}")     
        print((rule ," ---- " ,self.token, " ---- " , self.predictionSets[rule]))     
  
  def pairing(self, expectedToken):    
    if not self.syntaxError and expectedToken != "epsilon":      
      if self.token["type"] == expectedToken:
        self.readNextToken()        
      else:
        self.syntaxError = True
        if self.token['type'] != '$':        
          print(f"Error sintáctico en {self.token['row']},{self.token['col']} , se esperaba {expectedToken}, se obtuvo {self.token['type']}")
        else:
          print(f"Error sintáctico , se esperaba {expectedToken}, se obtuvo {self.token['type']}")
  
  def checkEOF(self):
    if self.syntaxError == False:
      if self.token["type"] == "$":
        print(f"No hay errores sintácticos")
      else:        
        print("Esta cadena no es aceptada")
        
        print(self.lastRule  , self.token["type"])

  def getPredictionsForNT(self, nonTerminal):    
    predictionForNT = {}
    for rule in self.rules:      
      if rule.split("->")[0].strip() == nonTerminal:
        predictionForNT[rule] = self.predictionSets[rule]
    return predictionForNT
  
  def parseTokenInfo(self,tokenValue):
    tokenFields = {}
    tokenFieldsList = tokenValue.replace("<" , "").replace(">" , "").split(",")
    tokenFields["type"] = tokenFieldsList[0].strip()
    tokenFields["row"] = tokenFieldsList[-2].strip()
    tokenFields["col"] = tokenFieldsList[-1].strip()
    if tokenFields["type"] in {"id", "text"}:
      tokenFields["value"] = tokenFieldsList[1].strip()
    if tokenFields["type"] in {'Stack','Program', 'TextWindow', 'Array' }:
      tokenFields["type"]  = "Reserved_Word"
    return tokenFields
   
a = syntaxAnalizer()
a.nonTerminal(a.grammar["Starting symbol"])
a.checkEOF()