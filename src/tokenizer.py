

# class that creates the symbol table from the tokens
# do I need to take care of escape sequences?
class tokenizer:
	def __init__(self):
		self.token_stream = []
		self.symbol_table = []
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
		self.spfuncs = ['printf']
	

	def tokenize(self, token_stream):

		string_state = False
		self.token_stream = token_stream
		buf = ''
		#print self.token_stream
		pop_list = []
		for i in range(0, len(self.token_stream)):
			if self.token_stream[i] == 'include' and self.token_stream[i+1] == '<':
				#include <stdio.h>
				if '.' in self.token_stream[i+3] and 'h' in self.token_stream[i+4]:
					libstrbuf = self.token_stream[i+2] + self.token_stream[i+3] + self.token_stream[i+4]
					self.token_stream[i+2] = libstrbuf
					self.token_stream[i+3] = 'DEL'
					self.token_stream[i+4] = 'DEL'
				
		while 'DEL' in self.token_stream:
			self.token_stream.remove('DEL')

		print 'HEREHERE', self.token_stream

		for i in self.token_stream:

			
			
			if i == '"' and string_state == False:
				string_state = True
				self.symbol_table.append({'token_type': 'punctuation', 'value': '"'})
				continue
			elif i == '"' and string_state == True:
				# create " token and add 'buf' as string literal token
				string_state = False
				#print buf
				self.symbol_table.append({'token_type': 'const', 'value': buf})
				self.symbol_table.append({'token_type': 'punctuation', 'value': '"'})
				buf = ''
				continue

			if string_state == True:
				buf += i

			


			elif i in self.keywords:
				self.symbol_table.append( {'token_type': 'keyword', 'value': i} )

			elif i in self.punctuation:
				self.symbol_table.append({'token_type': 'punctuation', 'value': i})

			elif i in self.incop:
				self.symbol_table.append({'token_type': 'incop', 'value': i})

			elif i in self.decop:
				self.symbol_table.append({'token_type': 'decop', 'value': i})

			elif i in self.arithop:
				self.symbol_table.append({'token_type': 'arithop', 'value': i})

			elif i in self.relop:
				self.symbol_table.append({'token_type': 'relop', 'value': i})

			elif i in self.asgnop:
				self.symbol_table.append({'token_type': 'asgnop', 'value': i})

			elif i in self.logop:
				self.symbol_table.append({'token_type': 'logop', 'value': i})

			elif i in self.bitop:
				self.symbol_table.append({'token_type': 'bitop', 'value': i})

			elif i in self.spfuncs:
				self.symbol_table.append({'token_type': 'spfuncs', 'value': i})

			elif '.c' in i or '.h' in i:
				self.symbol_table.append({'token_type': 'const', 'value': i})

			else:
				try: # check for number
					float(i)
					self.symbol_table.append({'token_type': 'const', 'value': i})				
				except ValueError: # else identifier
					self.symbol_table.append({'token_type': 'identifier', 'value': i})	
					
			
	
		#self.symbol_table.append(token_stream)
		return self.symbol_table	