// Function SimpleFunction.test
(SimpleFunction.test)
// Pushing constant 0
@0
D=A
@0
A=M
M=D
@0
M=M+1
// Pushing constant 0
@0
D=A
@0
A=M
M=D
@0
M=M+1
// Pushing local 0
@0
D=A
@1
A=M
A=D+A
D=M
@0
A=M
M=D
@0
M=M+1
// Pushing local 1
@1
D=A
@1
A=M
A=D+A
D=M
@0
A=M
M=D
@0
M=M+1
// Arithmetic: add
@0
M=M-1
@0
A=M
D=M
@0
A=M-1
M=D+M
// Arithmetic: not
@0
A=M-1
M=!M
// Pushing argument 0
@0
D=A
@2
A=M
A=D+A
D=M
@0
A=M
M=D
@0
M=M+1
// Arithmetic: add
@0
M=M-1
@0
A=M
D=M
@0
A=M-1
M=D+M
// Pushing argument 1
@1
D=A
@2
A=M
A=D+A
D=M
@0
A=M
M=D
@0
M=M+1
// Arithmetic: sub
@0
M=M-1
@0
A=M
D=M
@0
A=M-1
M=M-D
// Returning
@1
D=M
@R13
M=D
@5
D=A
@R13
D=M-D
A=D
D=M
@R14
M=D
@0
M=M-1
A=M
D=M
@2
A=M
M=D
@2
D=M
@0
M=D+1
@1
D=A
@R13
D=M-D
A=D
D=M
@4
M=D
@2
D=A
@R13
D=M-D
A=D
D=M
@3
M=D
@3
D=A
@R13
D=M-D
A=D
D=M
@2
M=D
@4
D=A
@R13
D=M-D
A=D
D=M
@1
M=D
@R14
A=M
0;JMP
@_1
(_1)
0;JMP
