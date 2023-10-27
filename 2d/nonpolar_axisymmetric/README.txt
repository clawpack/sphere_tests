
Axisymmetric test with flat bottom and axis of symmetry passing through (0,0).

The initial conditions are a Gaussian ring with peak 20 degrees offset from
axis, as specified in qinit.f90.

The code in 1d_latitude computes the axisymmetric solution.  The initial ring
specified in 1d_latitude/qinit.f90 is has a peak at 70 degrees, which is
offset 20 degrees from the pole.  This solution is read in by setplot.py to
produce a comparison with the scatter plot of the 2d solution.
