# ALPACA_from_terminal
Python code to launch ALPACA/MALPACA in a batch terminal procedure

ALPACA is a Slicer plugin (SlicerMorph)
See demo for use https://www.youtube.com/watch?v=ZRikzsUBeAE
and description here https://github.com/SlicerMorph/Tutorials

This code aims at launching the ALPACA calculation from a terminal or from the Slicer Python console (to speed up the process or parallelise the calculations)
With this example code "alpaca_on_terminal_hamsters.py" :
Two options
(1)From the terminal : 
Do
"C:\Users\ch1371gu\AppData\Local\NA-MIC\Slicer 5.2.2\Slicer.exe" --no-splash --no-main-window --python-script "alpaca_on_terminal_hamsters.py"
Note that according to the paths you indicate, you should be inside your Slicer folder and your "alpaca_on_terminal.py" file as well 

(2) From the Slicer Python console: 
Put the "alpaca_on_terminal.py" file inside the Slicer directory ("C:\Users\ch1371gu\AppData\Local\NA-MIC\Slicer 5.2.2\Slicer.exe")
and from the Slicer Python console do : 
exec(open("alpaca_on_terminal_hamsters.py").read())
