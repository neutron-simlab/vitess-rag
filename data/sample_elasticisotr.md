# VITESS Module 'sample_elasticisotr' for isotropic scattering

This module simulates a sample scattering isotropically and elasticly (conforming to a delta-function at energy 0), which can have the following geometries: cuboid, sphere, cylinder or hollow cylinder.

In VITESS 3.n, the parameter input is separated between direct input parameters that are given on the main window and others that are stored in a file ('File input parameters'). In VITESS 4.n, all parameters can be given as direct input parameters, but using the file is still possible. If a parameter is given in both ways, the direct input parameter will be used.

The probability weight *P* provided by the former module is multiplied by the following factors:

$$
P' = P \times \left(1 - \exp(-\mu_s d)\right) \times \mathrm{Attenuation} \times \frac{\mathrm{solid\ angle}}{4\pi}
$$

where μ_s = σ_s ρ is the macroscopic scattering coefficient [cm⁻¹], i.e. the scattering cross section σ multiplied by the particle density ρ. *Attenuation* means a wavelength and path length (before and after the scattering) dependent exponential factor:

$$
\mathrm{Attenuation} = \exp\left(-\mu_{abs} \times \mathrm{pathlength}\right), \quad \mu_{abs} \sim \lambda
$$

And the usual tabulated value for 1.798 Å has to be converted to 1 Å in order to calculate the input value *absorption coeff.*

Note that there is currently no beam of unscattered neutrons - even if the scattering probability is low.

The sample structure is considered as homogeneous and absorbent. The geometrical parameters of the sample are: position, horizontal and vertical offset angles with reference to the final coordinate system of the antecedent module, and size of the sample.

Detailed parameter definitions can be read from the tables below.

In the output frame X'Y'Z', all neutron coordinates are referring to the moment when the neutrons are just crossing the sample walls after the scattering. Multiple scattering is not yet included. The effect of sample size and geometry on the scattered intensity can be calculated by calibration taking into account that *I / I'* = *V/V'* (*V* - illuminated sample volume).

## The following table lists the main parameters of the module 'sample_elasticisotr':

| Parameter  Unit | Description | Range or Values | Command Option |
|---|---|---|---|
| parameter file | Includes FILE INPUT PARAMETERS. This file can be read or created/modified by the VITESS shell. | sampleelastizotr_default.iso | -P |
| colour  [-] | if -1, all neutrons are scattered <br>if not, only neutrons of this color are scattered | ≥ -1 | -c |
| repetition  [-] | If this integer >1, the neutron trajectory is used multiple times to obtain better statistics. | ≥ 1 | -A |

## The following table lists the file input parameters of the module 'sample_elasticisotr':

| Parameter  Unit | Description | Range or Values | Command Option |
|---|---|---|---|
| angle horiz final<br>angle vert final  [deg] | horizontal and vertical angles θ and φ defining the mean scattering direction | -180° - 180° | -E <br>-F |
| delta angle horiz<br>delta angle vert  [deg] | Angular widths Δθ and Δφ of the horizontal and vertical scattering direction <br>If read from file, Δθ and Δφ are regarded as the full ranges, i.e. scattering takes place in the range [θ - ½ Δθ, θ+ ½ Δθ],[φ - ½ Δφ,φ + ½ Δφ] <br>If given as input parameter (VITESS 4), Δθ and Δφ are regarded as the ranges around the mean angles, i.e. scattering takes place in the range [θ - Δθ, θ + Δθ],[φ - Δφ,φ + Δφ] | 0° - 360° or <br>0° - 180° (param.) | -e <br>-f |
| scattering coefficient  [1/cm] | Macroscopic total scattering cross section of the sample <br>This is: density × scattering cross section | from tables | -T |
| absorption coefficient  [1/cm/Å] | Macroscopic absorption cross section of the sample per wavelength <br>This is the attenuation constant per unit wavelength (corresponding to 1 Angstrom) <br>It is: density × absorption cross section. | > 0 | -m |
| position X<br>position Y<br>position Z  [cm] | Position of the sample center (in the frame provided by the former module). | e.g. 10.0, 0.0, 0.0 | -x <br>-y <br>-z |
| sample geometry | Geometry of the sample <br>On the command line it is an integer; 0 (no geometry) stops the module with the error 'Sample geometry missing' | 1: cuboid <br>2: cylinder <br>3: sphere <br>4: hollow cylinder <br>(in the parameter file by name: cuboid, cylinder, sphere, hollow-cylinder) | -G |
| thickness<br>height<br>width  [cm] | Thickness, height and width give dimensions of a cuboid sample. For cylinder, only diameter and height are relevant parameters. For hollow cylinder, the inner diameter is given by the third parameter. For spherical samples, the first value is considered as the diameter. | e.g. cylinder: 0.5, 2.0 | -t <br>-h <br>-w |
| offset angle horizontal<br>offset angle vertical  [deg] | A rotation first around the Z axis and then around the (new)Y axis gives the orientation of the sample. It has no relevance for a spherical sample geometry. | e.g. 0.0, 0.0 | -o <br>-O |
| output frame X'<br>output frame Y'<br>output frame Z'  [cm] | The position of the output frame origin in the original frame. It represents the translation vector applied to shift the origin of the original (input) frame to the new (output) position. | one point on the scattered beam axis | -X <br>-Y <br>-Z |
| output angle horizontal<br>output angle vertical  [deg] | A rotation about the Z axis and then a rotation about the (new)Y axis defines a new orientation for the neutrons written to the output. | e.g. forward scattering: <br>0.0, 0.0 | -u <br>-U |
