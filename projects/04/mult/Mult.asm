// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

// this seems like pretty straightforward
//   if we look at the compute instructions, we do not have a multiply.
//   multiply is iterated addition so we will have to pick one number to loop over and add the other

//   we already have a sort of template for loop adding, since we have that example for 1+...+100
//   we just need to modify that to be R0+...+R0(R1 times) or R1+...+R1(R0 times)

//   initialize counter
@i
M=1

//initialize product to 0
@R2
M=0

(LOOP)
  // get current value of counter
  @i
  D=M
  // subtract R1 from current value of counter
  @R1
  D = D - M
  @END
  D;JGT //if i > R1, jump to (END)
  @R0
  D=M
  @R2
  M = D+M // add R0(summand being looped over R1 times) to R2(result)
  @i
  M=M+1 //increment counter
  @LOOP
  0;JMP //back to beginning of loop
(END)
  @END
  0;JMP
