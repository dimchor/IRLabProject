import enum
from index import InvertedIndex
from textprocessing import TextProcessing

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
        self.value: any = value

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
        

class DeMorgan:
    def __init__(self, tokens: list[Token]):
        self.__tokens = tokens
        self.__it = 0
    
    def __this(self) -> Token:
        return self.__tokens[self.__it]
    
    def __prev(self) -> Token:
        return self.__tokens[self.__it - 1]

    def __next(self) -> Token:
        return self.__tokens[self.__it + 1]
    
    def __del_this(self) -> None:
        del self.__tokens[self.__it]
    
    def __incr(self):
        self.__it += 1

    def __not_done(self) -> bool:
        return self.__it < len(self.__tokens)
    
    def __apply(self):
        del self.__tokens[self.__it - 1]
        bracket_depth = 1
        while bracket_depth > 0:
            if self.__this().type == TokenType.NOT:
                self.__del_this()
                if self.__this().type == TokenType.LBRACKET:
                    while self.__this().type != TokenType.RBRACKET:
                        self.__incr()
                    self.__incr()
                else:
                    self.__incr()
            if self.__this().type == TokenType.OR:
                self.__this().type = TokenType.AND
                self.__this().value = '&'
                self.__incr()
            if self.__this().type == TokenType.STRING:
                self.__tokens.insert(self.__it, Token(TokenType.NOT, '!'))
                self.__it += 2
            if self.__this().type == TokenType.LBRACKET:
                bracket_depth += 1
                self.__incr()
            if self.__this().type == TokenType.RBRACKET:
                bracket_depth -= 1
                self.__incr()
                continue
            if self.__this().type == TokenType.AND:
                if self.__prev().type == TokenType.RBRACKET:
                    inner_it = self.__it - 2
                    inner_bracket_depth = 1
                    while inner_bracket_depth > 0:
                        if self.__tokens[inner_it].type == TokenType.RBRACKET:
                            inner_bracket_depth += 1
                        if self.__tokens[inner_it].type == TokenType.LBRACKET:
                            inner_bracket_depth -= 1
                        inner_it -= 1
                    self.__tokens.insert(
                        inner_it, Token(TokenType.LBRACKET, '('))
                    self.__incr()
                else:
                    inner_it = self.__it - 1
                    if inner_it - 1 >= 0 and \
                        self.__tokens[inner_it - 1].type == TokenType.NOT:
                        inner_it -= 1
                    self.__tokens.insert(
                        inner_it, Token(TokenType.LBRACKET, '('))
                    self.__incr()
                if self.__next().type == TokenType.LBRACKET:
                    inner_it = self.__it + 2
                    inner_bracket_depth = 1
                    while inner_bracket_depth > 0:
                        if self.__tokens[inner_it].type == TokenType.LBRACKET:
                            inner_bracket_depth += 1
                        if self.__tokens[inner_it].type == TokenType.RBRACKET:
                            inner_bracket_depth -= 1
                        inner_it += 1
                    self.__tokens.insert(
                        inner_it + 1, Token(TokenType.RBRACKET, ')'))
                else:
                    inner_it = self.__it + 1
                    if self.__tokens[inner_it].type == TokenType.NOT:
                        inner_it += 1
                    if self.__tokens[inner_it].type == TokenType.LBRACKET:
                        inner_it += 1
                        while self.__tokens[inner_it].type != \
                            TokenType.RBRACKET:
                            inner_it += 1
                    else:
                        inner_it += 1

                    self.__tokens.insert(
                        inner_it, Token(TokenType.RBRACKET, ')'))
                self.__this().type = TokenType.OR
                self.__this().value = '|'
                bracket_depth += 1
                self.__incr()

    def convert(self) -> list[Token]:
        last_not_index = -2
        while self.__not_done():
            if self.__this().type == TokenType.NOT:
                last_not_index = self.__it
                self.__incr()
            if self.__this().type == TokenType.LBRACKET and \
                last_not_index == self.__it - 1:

                # apply DeMorgan
                self.__apply()
                continue
            self.__incr()
        return self.__tokens

def convert_to_sets(tokens: list[Token], index: InvertedIndex) -> list[Token]:
    it = 0
    while it < len(tokens):
        if tokens[it].type == TokenType.NOT:
            del tokens[it]
            tokens[it].value = set(index.not_contains(tokens[it].value))
        elif tokens[it].type == TokenType.STRING:
            tokens[it].value = set(index.contains(tokens[it].value))
        it += 1
    return tokens

class Evaluate:
    def __init__(self, tokens: list[Token]):
        self.__tokens = tokens
        self.__operands = []
        self.__operators = []

    def __process(self):
        operator = self.__operators.pop()

        match operator.value:
            case '&':
                operand_rhs = self.__operands.pop().value
                operand_lhs = self.__operands.pop().value
                self.__operands.append(Token(
                    TokenType.STRING, operator_and(operand_rhs, operand_lhs)))
            case '|':
                operand_rhs = self.__operands.pop().value
                operand_lhs = self.__operands.pop().value
                self.__operands.append(Token(
                    TokenType.STRING, operator_or(operand_rhs, operand_lhs)))
            case _:
                pass

    def evaluate_infix(self) -> set[int]:

        for token in self.__tokens:
            match token.type:
                case TokenType.STRING:
                    self.__operands.append(token)
                case TokenType.LBRACKET:
                    self.__operators.append(token)
                case TokenType.RBRACKET:
                    if self.__operators[-1].type != TokenType.LBRACKET:
                        self.__process()
                    self.__operators.pop()
                case _:
                    while len(self.__operators) > 0 and \
                        self.__operators[-1].type <= token.type:
                        self.__process()
                    self.__operators.append(token)
        
        while len(self.__operators) > 0:
            self.__process()

        return self.__operands[-1].value

class LinguisticProcessor:
    def __init__(self, tokens: list[Token]):
        self.__tokens = tokens
        self.__it = 0
    
    def __this(self) -> Token:
        return self.__tokens[self.__it]
    
    def __prev(self) -> Token:
        return self.__tokens[self.__it - 1]
    
    def __del_this(self) -> None:
        del self.__tokens[self.__it]
    
    def __incr(self):
        self.__it += 1

    def __decr(self):
        self.__it -= 1
    
    def __len__(self) -> int:
        return len(self.__tokens)

    def __not_done(self) -> bool:
        return self.__it < len(self)
    
    def __remove_prev(self) -> bool:
        if self.__it - 1 < 0:
            return False
        match self.__prev().type:
            case TokenType.AND | TokenType.OR:
                self.__decr()
                self.__del_this()
            case TokenType.NOT:
                self.__decr()
                self.__del_this()
                return self.__remove_prev()
            case _:
                return False
        return True

    def __remove_empty_string(self):
        # remove previous tokens 
        removed = self.__remove_prev()
        # remove the empty string token
        self.__del_this()
        if len(self) == 0 or self.__it >= len(self):
            return

        # remove next tokens
        if not removed:
            match self.__this().type:
                case TokenType.AND | TokenType.OR:
                    self.__del_this()
                case _:
                    pass
     
    def apply(self, process_token) -> list[Token]:
        while self.__not_done():
            if self.__this().type != TokenType.STRING:
                self.__incr()
                continue

            if len(self.__this().value) == 0:
                self.__remove_empty_string()
                continue

            processed_tokens = TextProcessing.process(self.__this().value, 
                                                      process_token)

            if len(processed_tokens) > 1:
                self.__del_this()
                if self.__it - 1 >= 0 and self.__prev().type == TokenType.NOT:
                    self.__decr()
                    self.__del_this()
                    self.__tokens.insert(self.__it, Token(TokenType.LBRACKET, 
                                                          '('))
                    self.__incr()
                    for i in range(len(processed_tokens)):
                        self.__tokens.insert(self.__it, Token(TokenType.NOT, 
                                                              '!'))
                        self.__incr()
                        self.__tokens.insert(self.__it, Token(
                            TokenType.STRING, processed_tokens[i]))
                        self.__incr()
                        if i < len(processed_tokens) - 1:
                            self.__tokens.insert(self.__it, Token(TokenType.OR, 
                                                              '|'))
                            self.__incr()
                    self.__tokens.insert(self.__it, Token(TokenType.RBRACKET, 
                                                          ')'))
                    self.__incr()
                    continue

                self.__tokens.insert(self.__it, Token(TokenType.LBRACKET, '('))
                self.__incr()
                for i in range(len(processed_tokens)):
                    self.__tokens.insert(self.__it, Token(TokenType.STRING, 
                                                          processed_tokens[i]))
                    self.__incr()
                    if i < len(processed_tokens) - 1:
                        self.__tokens.insert(self.__it, Token(TokenType.AND, 
                                                              '&'))
                        self.__incr()
                self.__tokens.insert(self.__it, Token(TokenType.RBRACKET, ')'))
                self.__incr()
            elif len(processed_tokens) == 1:
                self.__this().value = processed_tokens[0]
                self.__incr()
            else:
                self.__remove_empty_string()
        return self.__tokens

def search(query: str, index: InvertedIndex, process_token) -> set[int]:
    tokens = Lexer(query).tokenize()
    check_syntax(tokens)

    tokens = DeMorgan(tokens).convert()

    tokens = LinguisticProcessor(tokens).apply(process_token)

    if len(tokens) == 0:
        raise Exception('Invalid input.')

    tokens = convert_to_sets(tokens, index)
    return Evaluate(tokens).evaluate_infix()
