import os.path
from tokenizer import *
import re

class lexer:
	# Function assigns param filepath to internal var, opens file
	# in read mode
	def __init__(self, filepath):
		self.filepath = filepath
		self.fileobj = open(filepath, 'r')
		self.filecontent = self.formatFile()
		self.setPatterns()
		self.setLexemePtrs()
		self.token_stream = []

	# Function that initialized patterns to look for as internal vars
	def setPatterns(self):
		self.keywords = ['auto', 'double', 'int', 'struct', 'break',
						'else', 'long', 'switch', 'case', 'enum',
						'register',	'typedef', 'char', 'extern', 'return',
						'union', 'const', 'float', 'short', 'unsigned',
						'continue', 'for', 'signed', 'void', 'default',
						'goto', 'sizeof', 'volatile', 'do', 'if', 'static',
						'while', 'include']

		self.punctuation = [',', '"', "'", ';', '.', '[', ']', '(', ')', '{', '}', '#']

		self.arithop = ['+', '-', '*', '/']
		self.incop = ['++']
		self.decop = ['--']
		self.relop = ['<', '<=', '>', '>=', '!=', '==']
		self.asgnop = ['=']
		self.logop = ['!', '||', '&&']
		self.bitop = ['|', '&', '^']
		self.bitLopOps = ['!', '||', '&&', '|', '&', '^']

	# Function that initializes lexeme beign and forward pointers
	def setLexemePtrs(self):
		self.lexemeBegin, self.lexemeForward = 0,0

	# Function replaces all tabs and newlines with whitespace,returns string
	def formatFile(self):
		_filecontent = self.fileobj.read()
		_filecontent = self.removeComments(_filecontent).replace('\n', ' ').replace('\t', ' ')
		return _filecontent

	# Function that removes all single line and multi-line comments
	# and returns a string that contains the contents of the file.
	def removeComments(self, _filecontent) :
		def blotOutNonNewlines( strIn ) :  # Return a string containing only the newline chars contained in strIn
			return "" + ("\n" * strIn.count('\n'))

		def replacer(match) :
			s = match.group(0)
			if s.startswith('/'):  # Matched string is //...EOL or /*...*/  ==> Blot out all non-newline chars
				return blotOutNonNewlines(s)
			else:                  # Matched string is '...' or "..."  ==> Keep unchanged
				return s

		pattern = re.compile(
			r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
			re.DOTALL | re.MULTILINE
			)

		return re.sub(pattern, replacer, _filecontent)

	# Token controller, called by parser, calls getTokenStream,
	# sends the tokenStream to the Tokenizer, which returns a symbol table
	# tokenController returns symbol table to parser
	# Format of this symbol table: all the tokens as they appeared in the code, repeats allowed
	# eg. int a; int b; : SYMBOL TABLE: int  a   ;   int    b  ;
	def tokenController(self):
		self.token_stream = self.getTokenStream()
		print self.filecontent
		#print '\n\nTOKEN STREAM GENERATED:', self.token_stream
		#print 'Now calling tokenizer'
		self.tokenizer = tokenizer()
		self.symbol_table = self.tokenizer.tokenize(self.token_stream)
		#print '\n\nSymTab: ', self.symbol_table
		return self.symbol_table

	# Function generates tokens based on patterns and returns them to tokenController
	# using a lexeme begin and forward ptr
	# need to implement lookaheads and count number of characters matched,
	# return token of the one that got the most matched characters, add to token stream
	def getTokenStream(self):
		token_stream = []
		skip_count = 0
		for i in range(0, len(self.filecontent)):
			if(skip_count > 0):
				skip_count -= 1
				continue

			self.lexemeForward += 1
			current_string = self.filecontent[self.lexemeBegin:self.lexemeForward]
			current_char = current_string[-1:]

			# delimited by spaces
			if self.filecontent[i] == ' ':
				self.lexemeBegin = self.lexemeForward

			# search for keywords
			if current_string in self.keywords:
				if self.filecontent[self.lexemeForward] == ' ':
					#print 'token keyword',current_string
					token_stream.append(current_string)
					self.lexemeBegin = self.lexemeForward

			elif current_string in self.punctuation:
				token_stream.append(current_string)
				self.lexemeBegin = self.lexemeForward

			elif current_string in self.arithop:
				if self.filecontent[self.lexemeBegin+1 : self.lexemeForward+1].replace(' ', '') == current_char:
					token_stream.append(current_char + self.filecontent[self.lexemeBegin+1 : self.lexemeForward+1])
					skip_count = 1
					self.lexemeForward += 1
				else:
					token_stream.append(current_string)
				self.lexemeBegin = self.lexemeForward

			elif current_string in self.relop:
				lookahead = i + 1
				lookahead_chars = 1
				while self.filecontent[lookahead] == ' ':
					lookahead += 1
					lookahead_chars += 1

				temp = self.filecontent[self.lexemeBegin:lookahead + 1]
				lookahead_chars += temp.count(' ')
				lookahead_string = temp.replace(' ', '')

				if lookahead_string in self.relop:
				    token_stream.append(lookahead_string)
				    self.lexemeForward += lookahead_chars
				    skip_count = lookahead_chars
				else:
				    token_stream.append(current_string)
				self.lexemeBegin = self.lexemeForward

			elif current_string in self.asgnop:
				if self.filecontent[self.lexemeBegin+1 : self.lexemeForward+1].replace(' ', '') == current_char:
					token_stream.append(current_char + self.filecontent[self.lexemeBegin+1 : self.lexemeForward+1])
					skip_count = 1
					self.lexemeForward += 1
				else:
					token_stream.append(current_string)
				self.lexemeBegin = self.lexemeForward

			elif current_string in self.bitLopOps:
				if self.filecontent[self.lexemeBegin+1 : self.lexemeForward+1].replace(' ', '') == current_char:
					token_stream.append(current_char + self.filecontent[self.lexemeBegin+1 : self.lexemeForward+1])
					skip_count = 1
					self.lexemeForward += 1
				elif current_char == '!' and self.filecontent[self.lexemeBegin+1 : self.lexemeForward+1].replace(' ', '') == '=' :
					token_stream.append('!=')
					skip_count = 1
					self.lexemeForward += 1
				else:
					token_stream.append(current_string)
				self.lexemeBegin = self.lexemeForward

			else:
				if (current_char.isalnum()) and self.filecontent[i + 1] == ' ':
 					token_stream.append(current_string)
 					self.lexemeBegin = self.lexemeForward
				elif self.inPunctuation(current_char) or self.inArithop(current_char) or self.inRelop(current_char):
 					token_stream.append(current_string[:-1])

 					if self.inArithop(current_char):
 						temp_lookahead_string = self.filecontent[self.lexemeBegin+1:self.lexemeForward+1]
 						if  temp_lookahead_string in self.incop or temp_lookahead_string in self.decop:
 							token_stream.append(temp_lookahead_string)
 							self.lexemeForward += 1
 							skip_count = 1
 					else:
 						token_stream.append(current_char)
 					self.lexemeBegin = self.lexemeForward
		return token_stream

	def inPunctuation(self, current_string_char):
		return current_string_char in self.punctuation

	def inArithop(self, current_string_char):
		return current_string_char in self.arithop

    def inRelop(self, current_string_char):
		return current_string_char in self.relop
