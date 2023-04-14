import sys
import collections

def read_input():
    """
    This function reads from standard input and stores the information in two sets and a dictionary.

    Returns:
        tuple: A tuple containing two sets and a dictionary.

    Example:
        >>> sys.stdin = io.StringIO('a,b,c\nd,e,f\nA -> B|C,D|E,F\n+, -, *, /\n')
        >>> read_input()
        ({'a', 'b', 'c'}, {'d', 'e', 'f'}, {'A': ['B', 'C,D', 'E,F']}, ['+', '-', '*', '/'])
    """
    
    # Read the first line of input and split it into its terminal symbols
    terminal_symbols = set(input().strip().split(','))   

    # Read the second line of input and split it into its non-terminal symbols
    non_terminal_symbols = set(input().strip().split(','))

    # Read the third line of input and split it into its grammar rules
    grammar_rules = input().strip().split(',')

    starting_symbol = input().strip()

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
  
    """
    This function computes the set of FIRST symbols for each non-terminal symbol in the given grammar.

    Args:
        terminal_symbols (set): A set of terminal symbols in the grammar.
        non_terminal_symbols (set): A set of non-terminal symbols in the grammar.
        grammar_dict (dict): A dictionary mapping non-terminal symbols to their production rules.

    Returns:
        dict: A dictionary mapping each non-terminal symbol to its set of FIRST symbols.

    Example:
        >>> terminal_symbols = {'a', 'b', 'c', 'd', 'e'}
        >>> non_terminal_symbols = {'S', 'A', 'B'}
        >>> grammar_dict = {'S': [['A', 'B'], ['a']],
                            'A': [['B', 'c'], []],
                            'B': [['d'], ['e']]}
        >>> compute_first_sets(terminal_symbols, non_terminal_symbols, grammar_dict)
        {'S': {'a', 'd', 'e'},
         'A': {'c', 'd', 'e'},
         'B': {'d', 'e'}}
    """

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
    changed = True   
    while changed:

      changed = False      
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
              changed = True
              if (hasEpsilon):
                first_sets[nonTerminal] |= {"epsilon"}    
         

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

def compute_follows_sets( first_sets, terminal_symbols, non_terminal_symbols, input_string):
  followingSet = {}
  
  # Initialize the FIRST sets for all non-terminal symbols to the empty set
  for symbol in non_terminal_symbols:
      followingSet[symbol] = set({})
  
  followingSet[startingSymbol] |= {"$"}

  changed = True
  while changed:    
    changed = False
    for nonTerminal in non_terminal_symbols:
      for leftHandSymbol , rules in grammar_dict.items():
        for rule in rules:
          for i in range(len(rule)):
            if rule[i] == nonTerminal:
              next = rule[i+1] if i < len(rule)-1 else "epsilon"
              toAdd  

              compute_rule_first_set


  
  

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

  print(Elements)

def main():
  readed = read_input()
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
  '''
  result4 = compute_rule_first_set(result2, result[0],result[1], "B C")
  print(result4)
  '''
main()