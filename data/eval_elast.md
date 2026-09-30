# VITESS Module 'eval_elast' for 1D Evaluation of Elastic Scattering

The module **eval_elast** is supposed to be used for elastic scattering (e.g. powder diffraction, SANS). The spectrum file will contain the neutron intensities counted for each channel of the evaluation interval (with respect to the evaluation parameter of interest).

There is an application which is useful especially for integrating the peak intensities of a powder spectrum within the evaluation interval. The integrated intensities are given in the *intensity file*, the ranges have to be defined in the *info file*. The info file has to be defined before running this module simply as a data file as follows: each integration range is defined with two numbers. The first number gives the centre of the integration interval (this corresponds e.g. to a powder peak), the second number defines the width of the integration interval. For each integration range a new line must be used. Example:

```text
0.1   0.2
0.3   0.1
```

First line means: integration between 0.0 and 0.2, the result of the integration refers to the interval centre 0.1. Second line means integration between 0.25 and 0.35, the result of the integration refers to the interval centre 0.3. Maybe one needs information from the spectra file to define the info file appropriately. Then a first run only to generate the spectrum file is recommended.

Note: the info file ranges must be defined appropriately that they lie within the evaluation interval!

## The following table lists the parameters of the module 'eval_elast':

| Parameter  Unit | Description | Range or Values | Command Option |
|---|---|---|---|
| evaluation parameter | Choose between 'd-spacing', 'momentum transfer Q', 'scattering angle' and 'difference between wavelength from TOF and true wavelength'. <br>On the command line it is an integer. | 1: d-spacing <br>2: momentum transfer Q <br>3: scattering angle <br>4: wavelength difference | -k |
| spectrum file | The name of the spectrum file, which will contain the evaluated data, has to be given. | - | -o |
| intensity file | Optional: It will contain the integrated intensities for certain ranges within the evaluation interval defined above. The ranges and the range centres have to be defined in the info file. | - | -O |
| info file | Optional: It is needed to define the integration ranges for an intensity file (see explanation and example in the text above). | - | -I |
| number of bins | The number of bins determines the segmentation of the d-spacing, momentum transfer, scattering angle, or wavelength difference and therewith the number of values written to the spectrum file. | ≥ 1 | -n |
| minimum <br>maximum  [Å] [1/Å] [deg] | The bounds of the interval for the evaluation parameter. <br>The unit follows the evaluation parameter: Å for d-spacing and wavelength difference, 1/Å for momentum transfer Q, deg for scattering angle. | ≥ 0 <br>max > min | -m <br>-M |
| increase to next bin  [%] | For a logarithmic binning the percentage has to be given by which the upper limit of each bin exceeds its lower limit. If this value is set, the parameter 'number of bins' is ignored | > 0 | -R |
| dead-spot  [deg] | (optional) All neutrons with a scattering angle (2θ) between 0 and dead-spot will not be considered in the evaluation. <br>It is only useful if the direct beam points to the detector (as in the case of SANS) and the module 'beamstop' is not used. | ≥ 0 | -d |
| probability weight | yes: (default) the attributed probabilities (due to the operations of the modules before) are considered <br>no : the probability weight of each neutron is considered with the weight 1 | 1: yes <br>0: no | -p |
| exclusive counts | yes: only the evaluated neutrons will be written to the VITESS output file (be considered by subsequent modules) <br>no : all are written to the output file | 1: yes <br>0: no | -c |
| scattering axis of the sample | In case the elastic sample scatters in one direction only, like e.g., the surface of a liquid that scatters only in z-direction, please specify this particular scattering axis (y or z). For isotropic scattering choose 'none'. | -1: none <br>1: y <br>2: z | -A |
| time of flight | yes: the wavelength is determined from the given flight path and the time-of-flight calculated for the trajectory (for TOF instruments) <br>no : the wavelength of all trajectories is supposed to be identical with the reference wavelength (for instruments on continuous sources) | 1: yes <br>0: no | -w |
| correct TOF to distance | yes: correct TOF for the flight path from sample center to the position of detection <br>no : use the given sample-detector distance | 1: yes <br>0: no | -t |
| flight path  [cm] | (for option TOF): Length of the total neutron flight path from point of t=0 setting (source or pulse shaping chopper) to detector | > 0 | -l |
| sample-detector distance  [cm] | nominal distance from sample to detector | > 0 | -D |
| time offset  [ms] | (for option TOF) global shift of the neutron time t → t − t_offset. It is used to shift the reference point for the time of flight analysis (e.g. by half the length of a long pulse). | ≥ 0 | -T |
| reference wavelength  [Å] | (for option: 'No TOF') The (average) wavelength set by velocity selector or monochromator <br>This module does not use the wavelength of the trajectory for data evaluation, but (as in real life) the wavelength given here. | > 0 | -r |
| time interval begin <br>time interval end  [ms] | (optional) The bounds of the time interval for the evaluation. <br>Only neutrons arriving in that time interval are considered in the evaluation, both for TOF and continuous instruments. | ≥ 0 <br>end > begin | -e <br>-E |
| colour | Only trajectories of the given color are evaluated. Color -1 or 'nothing' means: all trajectories are evaluated | ≥ -1 | -C |
