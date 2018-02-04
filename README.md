# Elecanisms 2018

## Setting up a sample project (Miniproject 0)
*Please note: This project, and most everything in this repo, requires an Elecanisms PIC24 Microcontroller board.*

  1. Fork and clone this repo to a sensible place on your computer
  2. Install the Compiler and SCons
     * Follow the instructions [here](http://elecanisms.olin.edu/handouts/1.1_BuildTools.pdf) to install the compiler and SCons
       _I've tested the Linux portion of this guide only. For Linux, you may also be required to install the 32_bit libraries described [here](http://microchipdeveloper.com/install:mplabx-lin64)_
     * Make note of the path to your compiler.
  3. Compile Your Project
     * Go to the project folder, blinkint
     * Open the SConstruct file and put the path to your compiler under "env.PrependENVPath"
     * Run SCons by typing "scons" into the terminal. You should generate a couple files, including a .hex file that we will use to program the board.
  4. Assemble and Connect Your Breadboard
     * Run 3.3V and ground to a breadboard from terminals on your Elecanisms board , labeled "VDD" and "GND" respectively.
     * Find a button and connect two adjacent legs to the power and ground you just ran. The ground should be connected through a pull-down resistor (I used 10k&#937;).
     * Connect the leg of the button across from ground to the DO digital I/O pin on the Elecanisms board.
     * The end should look like this: 
     ![ ](https://raw.githubusercontent.com/audreywl/elecanisms2018/master/blinkint/breadboard.jpg)
  5. Setup the Bootloader
     * Follow the instructions on the README at https://github.com/audreywl/elecanisms2018/tree/master/bootloader
       _Again, I've only tested the Linux portion of this guide_
  6. Program Your Board  
     * Connect your Elecanisms board to your computer with a mini USB cable. You will use this to program the board, but will also need to keep it plugged in to power the board after programming, or switch to a similar power source.
     * Put the board in "bootloader mode" by holding down SW1 while hitting the red reset button. For more on the functions on the Elecanisms board, see its [documentation](http://elecanisms.olin.edu/handouts/1.4_board_notes.pdf).
     * Open the bootloader by navigating to the bootloader folder and typing "python bootloadergui.py" into the terminal.
     * If your board isn't recognized automatically, make sure you've put it in bootloader mode and hit Connect
     * In the bootloader GUI, go to File>Import Hex
     * Navigate to the blinkint folder and select the .hex file we generated in step 3.
     * Hit Write to write the .hex to the board and Disconnect/Run to run it.
