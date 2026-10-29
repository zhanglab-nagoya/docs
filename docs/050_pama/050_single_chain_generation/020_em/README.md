# Energy minimization

Polyply's output structure (`000_polyply/default.gro`) is geometrically sensible but not
physically relaxed — building a chain atom-by-atom with a random walk can easily leave a few
atoms slightly too close together. Running dynamics directly on such a structure would produce
enormous (unphysical) forces and the simulation would blow up. **Energy minimization (EM)**
fixes this: it moves atoms downhill in potential energy (here via the steepest-descent algorithm,
`integrator = steep` in `em.mdp`) until the maximum force on any atom drops below a threshold
(`emtol = 1000` kJ/mol/nm) or a step limit is hit (`nsteps = 50000`) — no temperature, no
trajectory of physical interest, just clash removal.

`em.mdp` also sets `constraints = h-bonds` with the LINCS algorithm: bonds to hydrogen atoms are
held perfectly rigid rather than modeled as (very stiff, very fast-oscillating) harmonic springs.
This is standard practice for any run with a 1+ fs timestep — vibrations of bonds to hydrogen are
otherwise the fastest motion in the system and would force an impractically small timestep.

## Provenance

    cp ../000_polyply/default.gro .
    cp ../000_polyply/system.top .
    cp ../000_polyply/custom-ffnonbonded.itp .
    cp ../000_polyply/molecule_with_pairs.itp molecule.itp
    cp -r ../000_polyply/oplsaa.ff .

(Note the rename on the last-but-one line: this step's `molecule.itp` is `000_polyply`'s
*pairs-fixed* topology, `molecule_with_pairs.itp` — see step 4 there.)

## Run

    gmx_mpi grompp -f em.mdp -c default.gro -p system.top -o em.tpr -maxwarn 1

`grompp` ("GROMACS preprocessor") combines the topology (`-p`), starting coordinates (`-c`), and
run parameters (`-f`) into a single self-contained binary run-input file, `em.tpr`. The
`-maxwarn 1` here overrides one specific, expected, harmless warning: because this is a single
isolated chain in a (comparatively) small simulation box, the box is smaller than twice the
nonbonded cutoff for some pairs of atoms excluded from each other by bonding, so GROMACS warns it
can't apply a long-range dispersion correction to them. This doesn't affect the minimization
itself; `-maxwarn` should never be used to blanket-suppress warnings you haven't actually read and
understood.

    export OMP_NUM_THREADS=1

    nohup mpirun -n 8 gmx_mpi mdrun -deffnm em > gmx.log 2>&1 &

`mdrun` actually performs the minimization described by `em.tpr`. `-n 8` splits the single
molecule's atoms across 8 MPI ranks (one simulation, parallelized — not 8 independent runs);
`OMP_NUM_THREADS=1` avoids additionally spawning OpenMP threads per rank, which would oversubscribe
the available CPU cores on top of the 8 MPI ranks. `-deffnm em` tells `mdrun` to name all its
output files with the `em` prefix (`em.gro`, `em.log`, …) instead of the default `md.*`. The
trailing `&` backgrounds the run and `nohup`/output redirection let it keep running and logging to
`gmx.log` even if your terminal session closes; for a system this small the run typically finishes
in well under a minute, so backgrounding it isn't strictly necessary, but it's a one-line habit
worth having for runs that will eventually be bigger.

`em.gro` — the minimized structure — is what gets carried forward into `030_nvt`.
