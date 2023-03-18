from Lexer import Lexer

if __name__ == "__main__":
    l = Lexer("./numeric.txt")
    l.readStream()
    #l.readFile()
    l.printTokens()
