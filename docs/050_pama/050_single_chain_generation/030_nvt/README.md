# NVT equilibration

Energy minimization only removes bad clashes — it leaves the structure at effectively 0 K, with
none of the thermal motion a real system would have. **NVT equilibration** (constant Number of
particles, Volume, and Temperature) runs actual molecular dynamics for a short time to bring the
structure up to a physically reasonable temperature and let it explore nearby conformations,
before you'd trust any measurement taken from it (or, as here, before feeding it onward to another
simulation engine).

`nvt.mdp` sets `integrator = md` (real Newtonian dynamics, vs. EM's artificial steepest-descent
minimization) with a 1 fs timestep for 200,000 steps (200 ps total). `tcoupl = v-rescale` with
`ref_t = 300` is a thermostat holding the system at 300 K; `gen_vel = yes` / `gen_temp = 300`
draws the *initial* atomic velocities from a Maxwell-Boltzmann distribution at 300 K (recall `em`
produced a structure with no velocities at all). `pcoupl = no` keeps the box size fixed — this is
*NVT*, not *NPT* (constant pressure), since there's no surrounding solvent/box content here for a
pressure coupling to act on meaningfully; just the single polymer chain in vacuum/a fixed box.

## Provenance

    cp ../020_em/custom-ffnonbonded.itp .
    cp ../020_em/em.gro default.gro
    cp ../020_em/molecule.itp .
    cp ../020_em/system.top .

## Run

    gmx_mpi grompp -f nvt.mdp -c default.gro -p system.top -o nvt.tpr -maxwarn 1

Same tool, same reason for `-maxwarn 1`, as in `020_em` — see that step's README for details.

    export OMP_NUM_THREADS=1

    nohup mpirun -n 8 gmx_mpi mdrun -deffnm nvt > gmx.log 2>&1 &

Same rationale as `020_em`'s `mdrun` invocation. This run takes noticeably longer than EM (it's
200,000 real MD steps rather than a quick minimization) — expect several minutes depending on your
hardware.

`nvt.gro` — the thermalized structure — is what gets carried forward into `050_conversion`.
