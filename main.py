from Lexer import Lexer

if __name__ == "__main__":
    l = Lexer("./smallBasicScript.txt")
    l.readStream()
    #l.readFile()
    l.printTokens()
