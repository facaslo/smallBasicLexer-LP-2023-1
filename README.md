<style>
  img{
    background-color: white;
  }
</style>


# Introduction
The following small Basic lexical analizer was built for the programming languages course from the Universidad Nacional de Colombia.
This implementation is based on the following automata 
![lexical analyzer automata](lex_automata.png "Title")
The arcs define the characters that the automata must read to pass to another state and the acceptance states are those surrounded by two circles.
The number that appears in the acceptance state between parenthesis, is the number of positions the buffer must move to the left once it has reached that state , then it must save the corresponding token in the following format: <tkn_type, [token value] , row , col>.
