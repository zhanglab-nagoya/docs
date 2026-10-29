# Per-atom force comparison

First, run single-point force evaluations with GROMACS and LAMMPS in sub folders.

Next, compare forces with

    $ bash compare_forces.sh 
    Max ΔF: 0.813808 atom 4125

Inspect the generated file

    $ head -n 4 force_compare.dat 
    1 242.675831 243.058874 0.400936
    2 442.119825 442.046842 0.096356
    3 361.428677 361.322891 0.113533
    4 203.187832 203.216066 0.034015

Columns are atom ID, gmx force vector magnitude, lmp force vector magnitude, gmx - lmp force vector diff magnitude.

The forces should agree closely for each atom.
