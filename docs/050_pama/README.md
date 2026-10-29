# PAMA

Notes and workflows for PAMA (poly(alkyl methacrylate)) molecules: random alkyl-methacrylate
copolymers built from an OPLS-AA monomer library, for use in classical molecular dynamics.

## Folder content

* `050_single_chain_generation`: build and equilibrate a single PAMA chain with `polyply` and
  `GROMACS`, then convert it to a `LAMMPS` input file with `InterMol`.
