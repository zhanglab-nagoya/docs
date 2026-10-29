# Conversion from GROMACS to LAMMPS

## Provenance

    cp ../030_nvt/custom-ffnonbonded.itp .
    cp ../030_nvt/nvt.gro default.gro
    cp ../030_nvt/molecule.itp .
    cp ../030_nvt/system.top .

## Environment

Created intermol venv with:

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

## Convert

Convert and evaluate energies with

    intermol-convert --gro_in default.gro system.top --lammps --oname converted --energy --lmppath $(which lmp) --gropath $GMXBIN --verbose

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

Note the absence of an `improper` row: earlier versions of the `oplsaaLigParGen` library parametrized each PAMA monomer's own backbone Cα=Cβ bond as a vinyl C=C double bond (an artifact of LigParGen treating each monomer as the free vinyl starting material), which carried spurious planarity impropers. The library now treats the backbone bond as the sp3 single bond it actually is once polymerized, so no impropers remain.

Next, compare per-atom forces with single-point force evaluations found within the `forces` sub folder.
