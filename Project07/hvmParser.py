"""
hvmParser.py -- Parser class for Hack VM translator
"""

from hvmCommands import *

class Parser(object):
    def __init__(self, sourceName, comments=None):
        """
        Open 'sourceFile' and gets ready to parse it.
        """
        self.file = open(sourceName, 'r');
        self.lineNumber = 0
        self.line = ''
        self.rawline = ''
        self.comments = comments

    def Advance(self):
        """
        Reads the next command from the input and makes it the current
        command.
        Returns True if a command was found, False at end of file.
        """
        while True:
            if self.file:
                self.rawline = self.file.readline()
                if len(self.rawline) == 0:
                    return False
                self.rawline = self.rawline.replace('\n', '')
                self.line = self.rawline
                i = self.line.find('//')                
                if i != -1:
                    if self.comments:
                        self.comments.Write('    '+self.line[i:])
                    self.line = self.line[:i]
                self.line = self.line.replace('\t', ' ').strip()
                if len(self.line) == 0:
                    continue
                self._Parse()
                return True
            else:
                return False

    def CommandType(self):
        """
        Returns the type of the current command:
            C_ARITHMETIC = 1
            C_PUSH = 2
            C_POP = 3
            C_LABEL = 4
            C_GOTO = 5
            C_IF = 6
            C_FUNCTION = 7
            C_RETURN = 8
            C_CALL = 9
        """
        return self.commandType
		
    def Arg1(self):
        """
        Returns the command's first argument.
        """
        return self.arg1

    def Arg2(self):
        """
        Returns the command's second argument.
        """
        return self.arg2

    """
    The function to be implemented. 
	For Project 6 the function should parse PUSH/POP and the arithmetic commands.
	Parses the current comment. Assumes that there is a single whitespace between the command and between each argument (there can be up to 2 arguments). 
	Fills in 'commandType', 'arg1' and 'arg2'.
    Some examples:
---------------------------------------------------------------------
|        currentLine	-> desired contents							|
---------------------------------------------------------------------
| "push constant 2"		-> arg1="constant", arg2=2		|
| "call yourfunction 3" -> arg1="yourfunction", arg2=3	|
| "and"					-> arg1="and", arg2=0				|
| "label xyz"			-> arg1="xyz"							|
---------------------------------------------------------------------
    """

    def _Parse(self):
        arithmetic = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
        command_types = {
                "arithmetic": C_ARITHMETIC,
                "push": C_PUSH,
                "pop": C_POP,
                "label": C_LABEL,
                "goto": C_GOTO,
                "if-goto": C_IF,
                "function": C_FUNCTION,
                "return": C_RETURN,
                "call": C_CALL
                }
        # command [arg1 [arg2]]
        self.commandType = None  #this should store the type of the command
        self.arg1 = None         #this should store the first argument of the command (if there is a first argument)
        self.arg2 = None         #this should store the second argument of the command (if there is a second argument)
        line = self.line.split(" ")
        match len(line):
            case 0:
                return
            case 1 | 2:
                if line[0] in arithmetic:
                    self.commandType = command_types["arithmetic"]
                else:
                    self.commandType = command_types[line[0]]
                if line[0] in ("label", "goto", "if-goto", "call", "function"):
                    self.arg1 = line[1]
                    self.arg2 = 0
                else:
                    self.arg1 = line[0]
                    self.arg2 = 0
            case 3:
                self.commandType = command_types[line[0]]
                self.arg1 = line[1]
                self.arg2 = line[2]
        # print(self.commandType, self.arg1, self.arg2)

