// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// we need some knowledge of the hardware to do this correctly
// in particular we need the number of memory locations in the screen so that we know how much to loop over

// it's also clear that we need an infinite outer loop
// and a branching on the result of some memory location (keyboard input)
//   do we want to branch into a full inner loop (full keyboard black/white each outer loop?)
//   likely not - instead, we probably want to keep track of "how full the screen is"
//   like a stack
//   and each outer loop, "is a key pressed"?  if yes, fill in one screenloc and increment stack count
//     if not, clear one screenloc and decrement stack count
//     hm
//     is this what we want?
//     otherwise, perhaps we wanna just branch into an inner loop that does the whole screen at once
//     honestly that would be easier, at least to start with, and might be more accurate
//     honestly the specification is a little fuzzy on this, probably either way is fine since the behavior would be very similar as long as the simulator is fast enough
// ok.  so @SCREEN is the starting memloc of screen.  what is the end loc?
//      256 rows, 512 pixels per row.  but each memloc has 16bit.  so 512/16=32 register per row
//      so 32 * 256 = 8192 register per screen
//      i think we ought to just write the inner loop first.  just write a program that blackens the entire screen first.
//      once that works, it's just writing a trivial outer loop that branches over 1 memloc.

//store the size of the screen

@8192
D=A
@scr
M=D


(OUTLOOP)


@i
M=1 //initialize innerloop counter to 1. this actually does need to be inside the outer loop.
@SCREEN
D=A
@sl
M=D //set value of sl to be the memory location of current coloring.

//read keyboard
@KBD
//use conditional jumps on M, I think
D=M
@LOOPWHT
D;JEQ //(white, if zero)
@LOOPBLK
D;JNE //(black, if not zero)

//note: on revision, I noticed that we could have just used a single inner loop
//  with an if/then branch at the coloring instruction
//  this 2-loop method provides the more general case when we'd maybe want to color in a completely different way

(LOOPWHT)

  //if counter is greater than 8192, go to end
  @i
  D=M
  @8192
  D=D-A
  @ENDWHT
  D;JGT
  //   (if counter is greater than 8192, go to end) 

  // current memloc
  
  @sl  //A=sl
  A=M  //A=M[sl]
  M=0 //whiten at A

  //increment sl, i
  @i
  M=M+1
  @sl
  M=M+1
  @LOOPWHT
  0;JMP

(ENDWHT)

(LOOPBLK)

  //if counter is greater than 8192, go to end
  @i
  D=M
  @8192
  D=D-A
  @ENDBLK
  D;JGT
  //   (if counter is greater than 8192, go to end) 

  //blacken current memloc
  
  @sl  //A=sl
  A=M  //A=M[sl]
  M=-1 //blacken at A

  //increment sl, i
  @i
  M=M+1
  @sl
  M=M+1
  @LOOPBLK
  0;JMP

(ENDBLK)
  
@OUTLOOP
0;JMP
    
