# Per-atom force comparison

The energy comparison in the parent step checks that GROMACS and LAMMPS agree on the *total*
potential energy, but two wrong forces could in principle cancel and still give a matching total.
This step closes that gap by evaluating the per-atom *force vectors* with both engines, on the
exact same structure, and comparing them atom-by-atom.

First, run single-point force evaluations with GROMACS and LAMMPS in sub folders (`single_point_gmx/`,
`single_point_lmp/`) — "single-point" meaning the structure isn't moved at all (zero MD steps);
each engine just computes forces once for the given coordinates. GROMACS reports forces in
kJ/(mol·nm); LAMMPS (in its `real` unit style, used here) reports them in kcal/(mol·Å). Each
subfolder's `extract_forces.sh` converts LAMMPS's output to GROMACS's units (×41.84, since
1 kcal/(mol·Å) = 4.184 kJ/mol ÷ 0.1 nm = 41.84 kJ/(mol·nm)) so the two can be compared directly.

Next, compare forces with

    $ bash compare_forces.sh 
    Max ΔF: 0.813808 atom 4125

Inspect the generated file

    $ head -n 4 force_compare.dat 
    1 242.675831 243.058874 0.400936
    2 442.119825 442.046842 0.096356
    3 361.428677 361.322891 0.113533
    4 203.187832 203.216066 0.034015

Columns are atom ID, gmx force vector magnitude, lmp force vector magnitude, gmx - lmp force
vector diff magnitude (all in kJ/(mol·nm)).

The forces should agree closely for each atom: here, individual atomic force magnitudes run into
the hundreds of kJ/(mol·nm), while the worst per-atom discrepancy across all ~4000+ atoms is well
under 1 kJ/(mol·nm) — a residual numerical mismatch (floating-point/rounding differences between
the two engines' implementations), not a sign of a conversion error. A real conversion bug would
typically show up as a handful of *outlier* atoms with discrepancies comparable to or larger than
the forces themselves (tens to hundreds of kJ/(mol·nm)), not a small, uniform background level
like this.
