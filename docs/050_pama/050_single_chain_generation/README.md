# Generate PAMA molecules

The contents of this folder illustrate how to generate arbitrary PAMA (poly(alkyl methacrylate))
molecules and retrieve a corresponding LAMMPS data file, ready for molecular dynamics (MD)
production runs.

## Pipeline overview

No single tool here can go directly from "I want this copolymer" to "a correct LAMMPS input
file", so the pipeline hops between four tools, each used for what it's best at:

1. **polyply** builds the all-atom topology and an initial 3D structure for an arbitrary
   (random) copolymer sequence from a small library of OPLS-AA monomer building blocks. It
   cannot itself run dynamics or write LAMMPS files.
2. **GROMACS** takes that initial structure — which is geometrically reasonable but not
   physically relaxed — and relaxes it: first by energy minimization (removing bad clashes),
   then by a short NVT equilibration (randomizing/thermalizing the structure at 300 K). GROMACS
   also happens to be the engine whose topology format `InterMol` understands best as an input.
3. **InterMol** converts the equilibrated GROMACS topology + coordinates into a LAMMPS data
   file, and as a side effect re-evaluates the potential energy in both GROMACS and LAMMPS so
   you can check the conversion didn't silently break anything.
4. **LAMMPS** is the actual target engine the resulting `.lmp` file is meant for (e.g. for
   larger-scale or GPU-accelerated production runs later on).

Each numbered subfolder below is one of these stages; later stages `cp` their inputs from the
previous stage's outputs (see each subfolder's "Provenance" section), so the whole pipeline is a
simple numerically-ordered chain:

* `000_polyply`: polymer generation
* `020_em`: energy minimization
* `030_nvt`: NVT equilibration
* `050_conversion`: conversion to LAMMPS with InterMol, including a per-atom force sanity check
  (`050_conversion/forces/`)

## A note on reproducibility

`polyply gen_seq` (used in `000_polyply`) draws the random copolymer composition without a fixed
random seed. Re-running the commands in this tutorial from scratch will therefore give you a
*different* random PAMA chain than the one whose intermediate files are checked into this
repository — same monomer composition and chain length, different random ordering. That's
expected, not a mistake: use the committed `sequence.json` if you want to reproduce the exact
numbers shown in the example outputs below.

## Prerequisites

You'll need working installations of `polyply` (specifically the
[`jotelha/polyply_1.0`](https://github.com/jotelha/polyply_1.0) fork's
`2026-10-28-PAMA-parameters` branch — the PAMA monomer library isn't in upstream polyply),
`GROMACS`, `InterMol`, and `LAMMPS`, all reachable on your `$PATH` (or loaded via your local
module system). Where a step depends on something environment-specific — e.g. whether your
GROMACS build provides `gmx` or only `gmx_mpi` — that's called out in the relevant subfolder.
