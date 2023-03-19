from lexer import Lexer

if __name__ == "__main__":
    l = Lexer("./input.txt")
    l.readStream()
    #l.readFile()
    l.printTokens()
