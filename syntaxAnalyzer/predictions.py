import sys
import collections

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
  print("Simbolos no terminales: ", grammar[0] )
  print("Simbolos Terminales: ", grammar[1] )
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

'''
def compute_follows_sets(first_sets , terminal_symbols, non_terminal_symbols, grammar_dict , startingSymbol):  
  firstSets = first_sets  
  followingSet = {}
  # Initialize the FIRST sets for all terminal symbols
  for symbol in terminal_symbols:        
      followingSet[symbol] = {symbol}

  # Initialize the FIRST sets for all non-terminal symbols to the empty set
  for symbol in non_terminal_symbols:
      followingSet[symbol] = set({})
  
  followingSet[startingSymbol].add("$")

  changed = True
  while changed:    
    changed = False
    for nonTerminal in non_terminal_symbols:
      for leftHandSymbol , rules in grammar_dict.items():
        for rule in rules:
          for i in range(len(rule)):
            if rule[i] == nonTerminal:
              next = rule[i+1] if i < len(rule)-1 else "epsilon" 
              toAdd = firstSets[next] - {"epsilon"}
              if not(toAdd.issubset(followingSet[nonTerminal])) and len(toAdd)>0:
                changed = True
                followingSet[nonTerminal] |= toAdd
              if "epsilon" in firstSets[next] and len(followingSet[leftHandSymbol]) > 0 and not followingSet[leftHandSymbol].issubset(followingSet[nonTerminal]) :
                changed = True
                followingSet[nonTerminal] |= followingSet[leftHandSymbol]

  return followingSet        

'''

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

def isLL1(predictionsSet, grammar_dict):  
  elements = [[key.strip().split("->")[0].strip(), value]  for key, value in predictionsSet.items()]
  joinedSets = {}
  ll1 = True
  for i in range(len(elements)):
    nonTerminal = elements[i][0]
    currentPredictionSet = elements[i][1]
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
  isLL1Grammar = isLL1(predictions,grammar_dict)
  return { 
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

  print(isLL1(predictions,grammar_dict))
 

#printGrammarSets()