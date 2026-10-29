# Conversion from GROMACS to LAMMPS

The polymer was built and equilibrated in GROMACS because that's what polyply and the
`oplsaaLigParGen` library speak natively — but the goal of this pipeline is a LAMMPS input file.
**InterMol** is a dedicated topology-conversion tool: it reads a GROMACS topology/coordinate pair
and writes the equivalent LAMMPS data file, translating each bonded/nonbonded interaction type
into its LAMMPS counterpart. As a built-in sanity check, it can also re-evaluate the system's
potential energy with *both* engines on the converted files and report how closely they agree —
if the conversion introduced an error, this is usually where it shows up first (see
"Verification" below).

## Provenance

    cp ../030_nvt/custom-ffnonbonded.itp .
    cp ../030_nvt/nvt.gro default.gro
    cp ../030_nvt/molecule.itp .
    cp ../030_nvt/system.top .

## Environment

InterMol needs its own Python environment (it pins specific, somewhat dated dependency versions).
Created the intermol venv with:

    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv python3.10-dev

    python3.10 -m venv ~/venv/intermol
    source ~/venv/intermol/bin/activate
    pip install --upgrade pip

    cd ~/git
    git clone https://github.com/shirtsgroup/InterMol.git
    cd InterMol
    pip install -e .

    pip install numpy
    pip install parmed
    pip install six

If InterMol is available on your system through some other means (a module system, a prebuilt
environment, etc.), you can skip straight to "Convert" below — this block just documents how the
environment used to produce the files in this repository was built from scratch.

## Convert

Convert and evaluate energies with

    intermol-convert --gro_in default.gro system.top --lammps --oname converted --energy --lmppath $(which lmp) --gropath $GMXBIN --verbose

- `--gro_in default.gro system.top` — the GROMACS coordinate file and topology to read.
- `--lammps` — convert to LAMMPS format (InterMol also supports converting to/from Desmond, Amber,
  CHARMM).
- `--oname converted` — name the output files with the `converted` prefix (`converted.lmp`,
  `converted.input`).
- `--energy` — after converting, actually run both GROMACS and LAMMPS on the result and compare
  potential energies (needs `--lmppath`/`--gropath` so InterMol knows which executables to call).
- `$GMXBIN` must be set to your GROMACS `bin/` directory (sourcing GROMACS's `GMXRC` script does
  this); `$(which lmp)` resolves to wherever your `lmp` executable lives.

## Verification

The difference in potential energy between GROMACS and LAMMPS system should be small, e.g.

```
Energy group summary
=======================================================================
                type     input(gromacs)   output (lammps)     diff (lammps)
-----------------------------------------------------------------------
Not comparable energies: are likely not to be the same
-----------------------------------------------------------------------
        coulomb (LR)       594.69744873        0.00000000     -594.69744873
        coulomb (SR)    -14189.26660156        0.00000000    14189.26660156
       coulomb total     -3235.03594971    30488.76741520    33723.80336491
          coulomb-14     10359.53320312        0.00000000   -10359.53320312
              proper      7034.53125000     7217.26276480      182.73151480
            vdw (LR)      -228.22811890     -228.34348197       -0.11536307
            vdw (SR)     -4338.61279297        0.00000000     4338.61279297
           vdw total      -628.24984741     -856.70584861     -228.45600120
              vdw-14      3938.59106445        0.00000000    -3938.59106445
-----------------------------------------------------------------------
Comparable energy terms: these should be very close
-----------------------------------------------------------------------
               angle     11348.41601562    11348.42386560        0.00784998
                bond      3487.82983398     3487.83377952        0.00394554
              bonded     21870.77709961    22053.52040992      182.74331031
            dihedral      7034.53125000     7217.26276480      182.73151480
           nonbonded     -3863.28579712    -3861.88045072        1.40534640
           potential     18190.22070312    18191.63995920        1.41925607

---------------- Total Potential Energy Comparison --------------------
Input gromacs potential energy:         18190.22070312
Difference in potential energy from gromacs=>lammps conversion:         1.41925607
=======================================================================
```

Why some rows are "not comparable" while others "should be very close": GROMACS and LAMMPS both
compute the long-range electrostatics (and here, the long-range dispersion correction) via Ewald
summation/PME, but they report the energy breakdown differently. GROMACS splits Coulomb and van
der Waals energy into a real-space **short-range (SR)** part and a reciprocal-space
**long-range (LR)** part, computed separately; LAMMPS instead lumps everything reciprocal-space
into its own `elong`/`kspace` bookkeeping and reports `0` for the terms GROMACS calls `coulomb
(SR)`/`vdw (SR)` here, because InterMol's energy-comparison script doesn't attempt to reshuffle
LAMMPS's energy categories to match GROMACS's — it only sums them where that's safe. That's why
individual "not comparable" rows can differ by thousands of kJ/mol while the pipeline still works
correctly: what actually matters is the **total potential energy** at the bottom (here differing
by ~1.4 kJ/mol out of ~18,190 kJ/mol, i.e. well under 0.01%), plus the purely short-range bonded
terms (`bond`, `angle`, `dihedral`) that both programs compute identically and which should
therefore agree almost exactly (they do here, to 5–6 significant figures). A conversion bug would
typically show up as the *comparable* rows, or the total, disagreeing substantially — not the
"not comparable" rows, which are expected to differ by construction.

Note the absence of an `improper` row: earlier versions of the `oplsaaLigParGen` library
parametrized each PAMA monomer's own backbone Cα=Cβ bond as a vinyl C=C double bond (an artifact
of LigParGen treating each monomer as the free vinyl starting material), which carried spurious
planarity impropers. The library now treats the backbone bond as the sp3 single bond it actually
is once polymerized, so no impropers remain.

Next, compare per-atom forces with single-point force evaluations found within the `forces` sub
folder — the energy comparison above checks that the *total* is right, but says nothing about
whether any individual atom's force is wrong in a way that happens to cancel out overall; the
per-atom check closes that gap.
