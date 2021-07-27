from app.shared.error import Error
from app.shared.tokens_definition import TokenType
from app.parser.nodes import *
from app.parser.tree import Tree


CONSTANTS = [TokenType.DECIMAL, TokenType.INTEGER, TokenType.FALSE, TokenType.TRUE]

class Parser:
  def __init__(self, lexer):
    self.lexer = lexer
    self.currentToken = None
    self.tokenLocation = None
    self.tree = Tree()
    self.nextToken()

  def nextToken(self):
    self.currentToken, self.tokenLocation = self.lexer.nextToken()

  def checkToken(self, tokens):
    if type(tokens) is list:
      return self.currentToken.key in tokens
    return self.currentToken.key == tokens

  def consumeToken(self, tokens):
    current = self.currentToken
    if self.checkToken(tokens): self.nextToken()
    else: self.abort(tokens)
    return current

  def abort(self, expecteds):
    symbol = self.currentToken.value if self.currentToken.key != TokenType.EOF else self.currentToken.key
    raise Error('Parser error', symbol, self.tokenLocation, self.lexer.text, expecteds)

  def parse(self):
    while not self.checkToken(TokenType.EOF):
      if (self.line()): continue
      self.abort([TokenType.IDENTIFIER] + CONSTANTS)
    print(self.tree)

  def line(self):
    if self.checkToken(TokenType.END_LINE): return self.endLine()
    elif self.checkToken(TokenType.IDENTIFIER):
      self.tree.registerNode(self.expression())
      return self.consumeToken(TokenType.END_LINE)
    elif self.checkToken(CONSTANTS):
      self.tree.registerNode(self.expression())
      return self.consumeToken(TokenType.END_LINE)

  def endLine(self):
    self.consumeToken(TokenType.END_LINE)
    while self.checkToken(TokenType.END_LINE):
      self.consumeToken(TokenType.END_LINE)
    return True

  def expression(self):
    return self.binaryOperation(self.andExpression, self.expression, TokenType.OR)

  def andExpression(self):
    return self.binaryOperation(self.notExpression, self.andExpression, TokenType.AND)

  def notExpression(self):
    if self.checkToken(TokenType.NOT):
      return UnaryNode(Node(self.consumeToken(TokenType.NOT)), self.notExpression())
    return self.boolOperators()

  def boolOperators(self):
    tokens = [TokenType.EQUAL, TokenType.DIFFERENT, TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL]
    return self.binaryOperation(self.mathExpression, self.boolOperators, tokens)

  def mathExpression(self):
    return self.binaryOperation(self.term, self.mathExpression, [TokenType.ADD, TokenType.SUBTRACT])

  def term(self):
    return self.binaryOperation(self.factor, self.term, [TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.REST])

  def factor(self):
    return self.binaryOperation(self.unary, self.factor, TokenType.ELEVATE)

  def binaryOperation(self, nextFunction, currentFunction, tokens):
    left = nextFunction()
    if self.checkToken(tokens):
      operation = self.consumeToken(tokens)
      return BinaryNode(left, Node(operation), currentFunction())
    return left

  def unary(self):
    if self.checkToken([TokenType.ADD, TokenType.SUBTRACT]):
      signal = self.consumeToken([TokenType.ADD, TokenType.SUBTRACT])
      return UnaryNode(Node(signal), self.unary())
    return self.value()

  def value(self):
    types = [TokenType.IDENTIFIER] + CONSTANTS 
    if self.checkToken(types):
      return Node(self.consumeToken(types))
    elif self.checkToken(TokenType.LEFT_PAREN):
      self.consumeToken(TokenType.LEFT_PAREN)
      binaryOperation = self.expression()
      self.consumeToken(TokenType.RIGHT_PAREN)
      return binaryOperation
    self.abort(types)
