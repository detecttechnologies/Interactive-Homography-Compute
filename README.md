
# Interactive-Homography-Compute

An interactive UI to undertake perspective/homography transformations

### Usage

First install all the libraries required for the code:  `pip install -r Requirements.txt`

The code can then be run with: `python Homography-MPC_Interface.py`

### Navigating the UI
Stages in the ui that needs to be followed after running the script:

1. **Upload video or a CSV or an image files or an image folder** 
Upload any of the above by clicking the upload button.

2. **If Homography radio button is selcted**
Left click to add a point, and Ctrl+Left click to remove the nearest marked points from the frame
Enter the calibration scale in the text boxes specified.
The matlabplot's are displayed. 

3. **If MPC-Line option is selected**
Draw a line with your mouse buttons by clicking the start point and the end point consecutively.

4. **If MPC-RoI option is selected**
Draw a rectangle with the mouse movement.

5. **If MPC-Direction of entry option is selected**
Same procedure to be followed as it, that was followed while drawing the line. We would be drawing an arrow instead of a line

After the figures are drawn acoording to the option, pressing a save button, will enable us to write in an csv. If the options that are selected from the upload button are a non-csv option, the software creates a csvby itself called 'Camera Calibration details' and stores all the enteries for ther.

While loading an image in ui, we will find green lines already present, which indicate that the figures where marked there previously when the software was used.
