import enum

def operator_or(lhs: set[int], rhs: set[int]) -> set[int]:
    return lhs.union(rhs)

def operator_and(lhs: set[int], rhs: set[int]) -> set[int]:
    return lhs.intersection(rhs)

class TokenType(enum.IntEnum):
    STRING   = 1
    NOT      = 2
    AND      = 4
    OR       = 8
    LBRACKET = 16
    RBRACKET = 32

class Token:
    def __init__(self, token_type: TokenType, value):
        self.type = token_type
        self.value = value

    def __str__(self) -> str:
        return f'[{self.type}, {self.value}]'

class InvalidTokenException(Exception):
    def __init__(self, token: str):
        self.__token = token
    
    def __str__(self) -> str:
        return f'Invalid token \'{self.__token}\''

class MissingEndQuoteException(Exception):
    def __init__(self, delim: str):
        self.__delim = delim
    
    def __str__(self) -> str:
        return f'Missing end quote <{self.__delim}>'

class UnexpectedTokenException(Exception):
    def __init__(self, token: str):
        self.__token = token

    def __str__(self):
        return f'Unexpected token \"{self.__token}\"'

class Lexer:
    def __init__(self, text: str):
        self.__text = text
        self.__it = 0

    def __this(self) -> str:
        return self.__text[self.__it]

    def __incr(self) -> None:
        self.__it += 1
    
    def __not_done(self) -> bool:
        return self.__it < len(self.__text)
    
    def __is_whitespace(self) -> bool:
        return self.__text[self.__it] in ' \r\n\t'
    
    def __parse_string(self, delim: str) -> str:
        self.__incr()
        string = str()
        while self.__this() != delim:
            string += self.__this()
            self.__incr()
            if not self.__not_done():
                raise MissingEndQuoteException(delim) 
        return string

    def tokenize(self) -> list[Token]:
        tokens = []
        while self.__not_done():
            if self.__is_whitespace():
                self.__incr()
                continue
            
            match self.__this():
                case '(':
                    tokens.append(Token(TokenType.LBRACKET, '('))
                case ')':
                    tokens.append(Token(TokenType.RBRACKET, ')'))
                case '!':
                    tokens.append(Token(TokenType.NOT, '!'))
                case '&':
                    tokens.append(Token(TokenType.AND, '&'))
                case '|':
                    tokens.append(Token(TokenType.OR, '|'))
                case '\"' | '\'':
                    tokens.append(Token(TokenType.STRING, 
                                  self.__parse_string(self.__this())))
                case _:
                    raise InvalidTokenException(self.__this())
                
            self.__incr()
        return tokens

def check_syntax(tokens: list[Token]) -> None:
    START = TokenType.STRING | TokenType.LBRACKET | TokenType.NOT

    expected = START

    bracket_count = 0
    for token in tokens:
        if not (token.type & expected):
            raise UnexpectedTokenException(token.value)
    
        match token.type:
            case TokenType.STRING:
                expected = TokenType.AND | TokenType.OR | TokenType.RBRACKET
            case TokenType.RBRACKET:
                if bracket_count == 0:
                    raise UnexpectedTokenException(token.value)
                bracket_count -= 1
                expected = TokenType.AND | TokenType.OR | TokenType.RBRACKET
            case TokenType.NOT:
                expected = TokenType.STRING | TokenType.LBRACKET
            case TokenType.LBRACKET:
                bracket_count += 1
                expected = START
            case TokenType.AND | TokenType.OR:
                expected = START
            case _:
                pass
    
    # START or TokenType.NOT
    if expected == START or expected == (TokenType.STRING | TokenType.LBRACKET):
        raise Exception("Expected \"(\", \"!\" or string")
    
    if bracket_count > 0:
        raise Exception("Missing one or more \")\"")
        