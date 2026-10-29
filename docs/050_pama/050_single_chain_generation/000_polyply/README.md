# Polyply

PAMA parameters for various monomer building blocks are found within the extended oplsaaLigParGen library at [https://github.com/jotelha/polyply_1.0/tree/2026-10-28-PAMA-parameters](https://github.com/jotelha/polyply_1.0/tree/2026-10-28-PAMA-parameters).

## Use

First, generate sequence with

    polyply gen_seq -from_string A:1:1:CH3n-1.0 B:58:1:MMA-1.0 C:69:1:LA-0.217,EH-0.493,ST-0.290 -o sequence.json -name PAMA_BLOCK -seq A B C A -connect 0:1:0-0 1:2:57-0 2:3:68-0

Next, generate topology with

    polyply gen_params -lib oplsaaLigParGen -o molecule.itp -name PAMA_BLOCK -seqf sequence.json

Place the user-provided `oplsaa.ff` force field directory and `custom-ffnonbonded.itp` (custom non-bonded parameters for the PAMA monomers) in the working directory.

Manually create a `system.top`, i.e.

    #include "oplsaa.ff/forcefield.itp"
    #include "custom-ffnonbonded.itp"
    #include "molecule.itp"
    [ system ]
    ; name
    Single PAMA block polymer

    [ molecules ]
    ; name  number
    PAMA_BLOCK 1

Next, generate coordinates with

    polyply gen_coords -p system.top -o default.gro -name PAMA_BLOCK -dens 300

Note that polyply does not generate 1-4 pairs correctly. Generate all 1-4 pairs from the topology with

    python generate_pairs_from_dihedrals.py -i molecule.itp -o pairs.dat

and insert them into the ITP file with

    python insert_custom_pairs_list.py -p pairs.dat -i molecule.itp -o molecule_with_pairs.itp

Double-check that charge of generated polymer is zero with

    python check_total_charge.py molecule.itp

Double-check molecular weight with

    $ python check_molecular_weight.py default.gro 
    Molecular weight: 23390.597 g/mol
    Composition:
       C: 1396
       H: 2540
       O: 254
