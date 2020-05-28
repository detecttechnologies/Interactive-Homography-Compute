# Interactive-Homography-Compute
An interactive UI to undertake perspective/homography transformations
The code needs to be run with a command:     python Calibrate_homography.py

Stages in the ui that needs to be followed:

1)**Upload video**
Upload any video ny clicking the upload button.

2)**Mark the points in the frame.** 
Event: Right mouse double click to mark the points in the frame. (Left mouse click for linux os) 
     : Left mouse double click to remove the marked points from the frame.(Ctrl+T fir linux os). (# Dont use this when there is no points marked in the frame)
        
3)**Giving clibration scale.**
Give the height and width scale of the rectangles as integers and press the calibrate button after it.

4)After the matlabplots window is opened, any of the three buttons can be pressed to revisit and any of the three windows. The .npz will be save in the same directory of the code on clicking the Save button.


