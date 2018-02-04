# Elecanisms 2018

## Setting up a sample project (Miniproject 0)
*Please note - this project, and most everything in this repo, requires an Elecanisms PIC24 Microcontroller board.

  1. Fork and clone this repo to a sensible place on your computer
  2. Install the Compiler and SCons
     * Follow the instructions [here](http://elecanisms.olin.edu/handouts/1.1_BuildTools.pdf) to install the compiler and SCons
     * Make note of the path to your compiler.
  3. Compile Your Project
     * Go to the project folder, blinkint
     * Open the SConstruct file and put the path to your compiler under "env.PrependENVPath"
     * Run SCons by typing "scons" into the terminal
  4. Assemble and Connect Your Breadboard
     * Run 3.3V and GND from your Elecanisms board to a breadboard
     * Find a switch and connect two adjacent
