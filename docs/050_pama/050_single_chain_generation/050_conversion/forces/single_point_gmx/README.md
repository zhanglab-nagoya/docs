# Single point GROMACS forces evaluation

`singlepoint.mdp` sets `nsteps = 0` and `nstfout = 1` — run zero MD steps, but do write out the
force on every atom for the (single) frame that exists. This gives the GROMACS-side reference
forces for the comparison described in the parent `forces/README.md`.

## Provenance

    cp ../../custom-ffnonbonded.itp .
    cp ../../default.gro .
    cp ../../system.top .
    cp ../../molecule.itp .

## Run

    gmx grompp -f singlepoint.mdp -c default.gro -p system.top -o singlepoint.tpr

    gmx mdrun -s singlepoint.tpr -deffnm singlepoint

    bash extract_forces.sh  # select system (0)

> **If `gmx: command not found`:** some GROMACS builds only provide the MPI-enabled binary,
> `gmx_mpi`, and have no plain `gmx` at all (a single-process, non-MPI run still works fine
> through `gmx_mpi` — it's the same program). If that's your situation, substitute `gmx_mpi` for
> `gmx` in all three commands above, including inside `extract_forces.sh`.

`extract_forces.sh` runs `gmx traj` to pull the per-atom forces out of the `.trr` trajectory file
into a plain-text `force.xvg`, then reformats that into `forces_gmx.dat` (one line per atom:
index, Fx, Fy, Fz in kJ/(mol·nm)). It will interactively prompt you to pick an atom group to
output forces for — group `0` ("System") is the whole molecule, which is what you want here.
