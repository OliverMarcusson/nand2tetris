"""
hvmCodeWriter.py -- Code Writer class for Hack VM translator
"""

import os
from hvmCommands import *

debug = False

class CodeWriter(object):
    
    def __init__(self, outputName):
        """
        Open 'outputName' and gets ready to write it.
        """
        self.file = open(outputName, 'w')
        self.SetFileName(outputName)

        self.labelNumber = 0
        self.callLabel = None
        self.cmpLabels = {}
        self.needHalt = True
        self.functionNames = []
        
        # Starting points for memory segments
        # self.sp = 256
        # self.static = 16
        # self.local = 300
        # self.argument = 400
        # self.this = 3000
        # self.that = 3500
        # self.pointer = 3
        # self.temp = 5
        #
        # self._WriteCode(f"@{self.sp}, D=A, @0, M=D")
        # self._WriteCode(f"@{self.local}, D=A, @1, M=D")
        # self._WriteCode(f"@{self.argument}, D=A, @2, M=D")
        # self._WriteCode(f"@{self.this}, D=A, @3, M=D")
        # self._WriteCode(f"@{self.that}, D=A, @4, M=D")

    def Debug(self, value):
        """
        Set debug mode.
        Debug mode writes useful comments in the output stream.
        """
        global debug
        debug = value

    def Close(self):
        """
        Write a jmp $ and close the output file.
        """
        if self.needHalt:
            if debug:
                self.file.write('    // <halt>\n')
            label = self._UniqueLabel()
            self._WriteCode('@%s, (%s), 0;JMP' % (label, label))
        self.file.close()


    def SetFileName(self, fileName):
        """
        Sets the current file name to 'fileName'.
        Restarts the local label counter.

        Strips the path and extension.  The resulting name must be a
        legal Hack Assembler identifier.
        """
        if (debug):
            self.file.write('    // File: %s\n' % (fileName))
        self.fileName = os.path.basename(fileName)
        self.fileName = os.path.splitext(self.fileName)[0]
        self.functionName = None


    def Write(self, line):
        """
        Raw write for debug comments.
        """
        self.file.write(line + '\n')

    def _UniqueLabel(self):
        """
        Make a globally unique label.
        The label will be _sn where sn is an incrementing number.
        """
        self.labelNumber += 1
        return '_' + str(self.labelNumber)

    # For functions
    def _LocalLabel(self, name):
        """
        Make a function/module unique name for the label.
        If no function has been entered, the name will be
        FileName$$name. Otherwise it will be FunctionName$name.
        """
        if self.functionName != None:
            return self.functionName + '$' + name
        else:
            return self.fileName + '$$' + name

    # For variables
    def _StaticLabel(self, index):
        """
        Make a name for static variable 'index'.
        The name will be FileName.index
        """
        return self.fileName + '.' + str(index)    


    def _WriteCode(self, code):
        """
        Write the comma separated commands in 'code'.
        """
        code = code.replace(', ', '\n')
        self.file.write(code + '\n')
    
    def WritePushPop(self, commandType, segment, index):
        def should_decrement_sp():
            skip_label = self._UniqueLabel()
            return f"@0, D=M, @256, D=D-A, @{skip_label}, D;JLE, @0, M=M-1, ({skip_label})" 
        segments = {
                "constant": "",
                "local": "@1, A=M",
                "this": "@3, A=M",
                "that": "@4, A=M",
                "pointer": "@3",
                "temp": "@5",
                "argument": "@2, A=M"
                }

        if segment == "static":
            if commandType == C_PUSH:
                self._WriteCode(f"// Pushing static {index}")
                self._WriteCode(f"@{self._StaticLabel(index)}, D=M, @0, A=M, M=D")
                self._WriteCode("@0, M=M+1")
            
            elif commandType == C_POP:
                self._WriteCode(f"// Popping to static {index}")
                self._WriteCode("@0, M=M-1")
                self._WriteCode("@0, A=M")
                self._WriteCode("D=M")
                self._WriteCode(f"@{self._StaticLabel(index)}")
                self._WriteCode("M=D")
            return

        if commandType == C_PUSH:
            self._WriteCode(f"// Pushing {segment} {index}")
            to_push = f"@{index}, D=A, {segments[segment]}, A=D+A"
            if segment == "constant":
                self._WriteCode(f"@{index}, D=A, @0, A=M, M=D")
            else:
                self._WriteCode(f"{to_push}, D=M, @0, A=M, M=D")
            self._WriteCode("@0, M=M+1") 
            
        if commandType == C_POP:
            self._WriteCode(f"// Popping to {segment} {index}")
            # self._WriteCode(should_decrement_sp())
            self._WriteCode("@0, M=M-1")
            pop_to = f"@{index}, D=A, {segments[segment]}, A=D+A"
            self._WriteCode(f"{pop_to}, D=A, @R13, M=D, @0, A=M, D=M, @R13, A=M, M=D")
    
    def WriteArithmetic(self, command):
        self._WriteCode(f"// Arithmetic: {command}")
        if not command in ("not", "neg"):
            self._WriteCode("@0, M=M-1")
        match command:
            case "add":
                self._WriteCode(f"@0, A=M, D=M, @0, A=M-1, M=D+M")
                
            case "sub":
                self._WriteCode(f"@0, A=M, D=M, @0, A=M-1, M=M-D")
                
            case "neg":
                self._WriteCode(f"@0, A=M-1, M=-M")
                
            case "eq":
                eq_label = self._UniqueLabel()
                ne_label = self._UniqueLabel()
                end_label = self._UniqueLabel()
                self._WriteCode(f"@0, A=M, D=M, @0, A=M-1, D=D-M, @{eq_label}, D;JEQ, @{ne_label}, D;JNE")
                self._WriteCode(f"({eq_label}), @0, A=M-1, M=-1, @{end_label}, 0;JMP")
                self._WriteCode(f"({ne_label}), @0, A=M-1, M=0, @{end_label}, 0;JMP, ({end_label})")
                
            case "gt":
                gt_label = self._UniqueLabel()
                end_label = self._UniqueLabel()
                self._WriteCode(f"@0, A=M-1, D=M, @0, A=M, D=D-M, @0, A=M-1, M=0")
                self._WriteCode(f"@{gt_label}, D;JGT, @{end_label}, 0;JMP, ({gt_label}), @0, A=M-1, M=-1, ({end_label})")
                
            case "lt":
                lt_label = self._UniqueLabel()
                end_label = self._UniqueLabel()
                self._WriteCode(f"@0, A=M-1, D=M, @0, A=M, D=D-M, @0, A=M-1, M=0")
                self._WriteCode(f"@{lt_label}, D;JLT, @{end_label}, 0;JMP")
                self._WriteCode(f"({lt_label}), @0, A=M-1, M=-1, ({end_label})")
                
            case "and":
                self._WriteCode(f"@0, A=M, D=M, @0, A=M-1, D=D&M, @0, A=M-1, M=D")
                
            case "or":
                self._WriteCode(f"@0, A=M, D=M, @0, A=M-1, D=D|M, @0, A=M-1, M=D")
                
            case "not":
                self._WriteCode(f"@0, A=M-1, M=!M")
        
    def WriteInit(self, sysinit = True):
        """
        Write the VM initialization code:
	To be implemented as part of Project 7
        """
        if not sysinit:
            return
        
        if (debug):
            self.file.write('    // Initialization code\n')
        self._WriteCode("// Initializing")
        self._WriteCode("@256, D=A, @0, M=D")
        self.WriteCall("Sys.init", 0)


    def WriteLabel(self, label):
        """
        Write Hack code for 'label' VM command.
	To be implemented as part of Project 7

        """
        self._WriteCode(f"({self._LocalLabel(label)})")

    def WriteGoto(self, label):
        """
        Write Hack code for 'goto' VM command.
	To be implemented as part of Project 7
        """
        # if self.functionName == None:
        #     label = f"{self.fileName}$${label}"
        # else:
        #     label = f"{self.functionName}${label}"

        if not label in self.functionNames and not "." in label:
            label = self._LocalLabel(label)

        self._WriteCode(f"@{label}, 0;JMP")

    def WriteIf(self, label):
        """
        Write Hack code for 'if-goto' VM command.
	To be implemented as part of Project 7
        """
        # if self.functionName == None:
        #     label = f"{self.fileName}$${label}"
        # else:
        #     label = f"{self.functionName}${label}"
        
        if not label in self.functionNames:
            label = self._LocalLabel(label)

        self._WriteCode(f"// If-goto {label}")
        self._WriteCode(f"@0, M=M-1, A=M, D=M, @{label}, D;JNE")

    def WriteFunction(self, functionName, numLocals):
        """
        Write Hack code for 'function' VM command.
	To be implemented as part of Project 7
        """
        self.functionNames.append(functionName)
        self._WriteCode(f"// Function {functionName}")
        self.functionName = functionName

        self._WriteCode(f"({functionName})")
        for _ in range(int(numLocals)):
            self.WritePushPop(C_PUSH, "constant", 0)


    def WriteReturn(self):
        """
        Write Hack code for 'return' VM command.
	To be implemented as part of Project 7
        """
        self._WriteCode("// Returning")
        self._WriteCode("@1, D=M, @R13, M=D") # Save addr of frame to R13
        self._WriteCode("@5, D=A, @R13, D=M-D, A=D, D=M, @R14, M=D") # Save ret to R14
        self._WriteCode("@0, M=M-1, A=M, D=M, @2, A=M, M=D")
        self._WriteCode("@2, D=M, @0, M=D+1")
        self._WriteCode("@1, D=A, @R13, D=M-D, A=D, D=M, @4, M=D")
        self._WriteCode("@2, D=A, @R13, D=M-D, A=D, D=M, @3, M=D")
        self._WriteCode("@3, D=A, @R13, D=M-D, A=D, D=M, @2, M=D")
        self._WriteCode("@4, D=A, @R13, D=M-D, A=D, D=M, @1, M=D")
        self._WriteCode(f"@R14, A=M, 0;JMP")
        # self.functionName = None

    def WriteCall(self, functionName, numArgs):
        """
        Write Hack code for 'call' VM command.
	To be implemented as part of Project 7
        """
        self._WriteCode(f"// Calling {functionName} with {numArgs} arguments")
        return_label = self._UniqueLabel()
        self._WriteCode(f"@{return_label}, D=A, @0, A=M, M=D, @0, M=M+1")
        self._WriteCode("@1, D=M, @0, A=M, M=D, @0, M=M+1")
        self._WriteCode("@2, D=M, @0, A=M, M=D, @0, M=M+1")
        self._WriteCode("@3, D=M, @0, A=M, M=D, @0, M=M+1")
        self._WriteCode("@4, D=M, @0, A=M, M=D, @0, M=M+1")
        
        self._WriteCode(f"@0, D=M, @2, M=D, @{numArgs}, D=A, @2, M=M-D, @5, D=A, @2, M=M-D")
        self._WriteCode("@0, D=M, @1, M=D")
        self.WriteGoto(functionName)
        self._WriteCode(f"({return_label})")

   
