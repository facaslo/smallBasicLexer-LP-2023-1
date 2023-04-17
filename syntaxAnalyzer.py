import sys
from lexer import Lexer
from predictions import returnInfo

def storeConsoleInput():
  return list(sys.stdin)

class syntaxAnalizer():    
  def __init__(self):
    self.consoleInput = storeConsoleInput()
    self.lex = Lexer(self.consoleInput)
    self.grammarString = '''id,tkn_number,tkn_plus,tkn_minus,tkn_times,tkn_div,tkn_equals,tkn_left_paren,tkn_right_paren,epsilon
S,A,B,C,D,BP,CP
S -> A | B, A -> id tkn_equals B , B -> C BP , BP -> tkn_plus C BP | tkn_minus C BP | epsilon, C -> D CP, CP -> tkn_times D CP | tkn_div D CP | epsilon, D -> tkn_left_paren B tkn_right_paren | tkn_number 
S''' 
        
    self.grammar = returnInfo(self.grammarString)        
    #print( self.grammar["Prediction sets"]  )
    #print()
    grammarSet = set()
    for key, value in self.grammar["Grammar"].items():        
        for i in range(len(value)):
          output = key + " -> " + " ".join(value[i])          
          grammarSet.add(output)
    
    self.grammar["Grammar"] = grammarSet    

    self.rules = self.grammar["Grammar"]
    self.predictionSets = self.grammar["Prediction sets"]    
    self.token = self.parseTokenInfo(self.lex.readNextToken())    
    self.syntaxError = False

    #print(self.grammar["Is LL1"])
      
  def nonTerminal(self , nonTerminalSymbol): 
   if not(self.syntaxError):
    predictionsForNT = self.getPredictionsForNT(nonTerminalSymbol)   
    for rule,predictionSet in predictionsForNT.items():      
      if self.token["type"] in predictionSet:
        print(rule ," ---- " ,self.token, " ---- " , self.predictionSets[rule])
        ruleSymbolsList = [symbol.strip() for symbol in rule.split("->")[1:][0].strip().split(" ")]
        if not(ruleSymbolsList == ["epsilon"]):
          for ruleSymbol in ruleSymbolsList:          
            if ruleSymbol in self.grammar["Terminal symbols"]:          
              #print("Terminal:", symbol)          
              self.pairing(ruleSymbol)
            elif ruleSymbol in self.grammar["Non terminal symbols"]:
              #print("Non terminal:", symbol)
              self.nonTerminal(ruleSymbol)          
            else:
              print("Error")
        else:
          continue         
          

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
    return tokenFields
  
  def pairing(self, expectedToken):    
    if not self.syntaxError:
      if self.token["type"] == expectedToken:
        readedToken = self.lex.readNextToken()
        if readedToken != None:
          self.token = self.parseTokenInfo(readedToken)
        else:                
          print("Ha finalizado el análisis sintáctico con éxito")
      else:
          self.syntaxError = True
          print(f"Error sintáctico en {self.token['row']},{self.token['col']} , se esperaba {expectedToken}, se obtuvo {self.token['type']}")
    
a = syntaxAnalizer()
a.nonTerminal("S")
# print("###################################################################")
# while (True):  
#   try:
#     print(a.token)
#     a.token = a.parseTokenInfo(a.lex.readNextToken()) 
#   except:
#     break
# print("Prediction sets: ", a.predictionSets)
# print("Grammar: ", a.grammar["Grammar"])
# print(a.grammar["Prediction sets"].keys() == a.grammar["Grammar"])
#print(a.getPredictionsForNT("S"))

