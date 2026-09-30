# VITESS Module 'screen' to monitor intensity distribution on a cylindrical or flat detector

There are two VITESS modules to simulate detectors. The module **screen** monitors the neutrons arriving on a flat or banana shaped detector surface considering only the binning of the detector cells. In contrast, the module **detector** simulates a 3D detector array consisting of rectangular or cylindrical elements. It considers detection efficiency and different resolution effects. In the **screen** module, the spatial distribution of the neutrons on the screen is written to an output file, while the **detector** module needs to be followed by a monitor module for that; but it enables writing event files.

The module **screen** monitors the spatial distribution of neutrons arriving on an infinitely thin detector surface for 2 simple geometries:

- (a) a rectangular shaped detector centered around the beam direction
- (b) a banana shaped or cylindrical detector with vertical symmetry axis, vertically centered around the beam axis.

The **screen** gives directly an output file of the intensity distribution over the detector, i.e. a monitor function is included.

## The following table lists the parameters of the module 'screen':

| Parameter  Unit | Description | Range or Values | Command Option |
|---|---|---|---|
| monitor file | The monitor output file contains the 2D intensity distribution on the detector | - | -O |
| geometry  [-] | The geometry parameter specifies the overall geometry of the detector, which can either be flat (i.e. rectangular) or cylindrical. <br>On the command line it is an integer. | 1: cylindrical <br>2: flat | -G |
| file format | Choose between matrix style and the 'xyz' representation (readable by gnuplot and other analysis software). <br>'compact' means a shorter header and fewer digits in the written float numbers of the simulated count rate values <br>'integer' means that detector counts are written to the matrix, they are obtained by multiplying the count rate and the measurement time given in the source module. If no value is given, 60 s are assumed. Note that the g2 program cannot handle integer values properly. | 0: matrix <br>1: xyz <br>2: matrix compact <br>3: xyz compact <br>4: matrix integer | -F |
| height  [cm] | Height of the detector, both for the rectangular and the banana shaped detector | > 0, e.g. 50 | -h |
| width  [cm] | Width of the rectangular detector. (Not used for the cylindrical detector geometry) | > 0, e.g. 300 | -w |
| distance  [cm] | Distance from the center of the detector area to the origin (0,0,0), i.e. the sample center. In case of a cylindrical detector, this is the cylinder radius. | > 0, e.g. 100 | -D |
| min. angle  [deg] | Angular range covered by a cylindrical or banana shaped detector (Not used for the rectangular detector geometry). | -180° - 180° | -a |
| max. angle  [deg] | Angular range covered by a cylindrical or banana shaped detector (Not used for the rectangular detector geometry). | -180° - 180° | -A |
| number of rows | Number of channels partitioning the detector height = number of vertical bins in the 2D monitor | ≥ 1 | -z |
| number of columns | Number of channels partitioning the detector width = number of horizontal bins in the 2D monitor | ≥ 1 | -y |
