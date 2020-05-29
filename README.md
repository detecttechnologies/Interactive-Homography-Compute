
# Interactive-Homography-Compute

An interactive UI to undertake perspective/homography transformations

### Usage

First install all the libraries required for the code:  `pip install -r requirements.txt`

The code can then be run with: `python Calibrate_homography.py`

### Navigating the UI
Stages in the ui that needs to be followed after running the script:

1. **Upload video**
Upload any video ny clicking the upload button.

2. **Mark the points in the frame**
Left mouse double click to remove the marked points from the frame.(Ctrl+ Left mouse button for linux os). (# Dont use this when there is no points marked in the frame)

3. **Giving clibration scale**
Give the height and width scale of the rectangles as integers and press the calibrate button after it.

4. After the matlabplot's window is opened, any of the three buttons can be pressed to revisit and any of the three windows. The .npz will be save in the same directory of the code on clicking the Save button.


