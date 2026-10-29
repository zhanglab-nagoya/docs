# Polyply

`polyply` builds an all-atom topology (`.itp`) and initial coordinates (`.gro`) for a polymer
chain from a sequence of monomer "residues" and a force-field library that defines each residue's
atoms, bonds, angles, dihedrals, and how consecutive residues link up. This step produces exactly
that for one PAMA chain — nothing here runs any dynamics yet; the structure polyply writes out is
geometrically plausible but not energetically relaxed (that's what `020_em`/`030_nvt` are for).

PAMA parameters for the various monomer building blocks (methyl, methacrylate, and several alkyl
ester side-chain monomers) are found within the extended `oplsaaLigParGen` library at
[https://github.com/jotelha/polyply_1.0/tree/2026-10-28-PAMA-parameters](https://github.com/jotelha/polyply_1.0/tree/2026-10-28-PAMA-parameters).
This is a fork of upstream polyply — the PAMA-specific monomers and backbone link definitions
don't exist anywhere else, so `polyply` must be installed from that branch for the `-lib
oplsaaLigParGen` step below to work at all.

## Use

### 1. Define the copolymer sequence

First, generate the residue sequence with

    polyply gen_seq -from_string A:1:1:CH3n-1.0 B:58:1:MMA-1.0 C:69:1:LA-0.217,EH-0.493,ST-0.290 -o sequence.json -name PAMA_BLOCK -seq A B C A -connect 0:1:0-0 1:2:57-0 2:3:68-0

This is the least self-explanatory command in the pipeline, so here's what each piece means:

- `-from_string` defines named *macros* — reusable fragments — in the form
  `<tag>:<#residues>:<#branches>:<residues>`, where `<residues>` is one or more
  `resname-probability` pairs (comma-separated, probabilities summing to 1). So:
  - `A:1:1:CH3n-1.0` — macro `A`: a single (`1`), linear (`1` branch), chain-end-capping `CH3n`
    residue (methyl group).
  - `B:58:1:MMA-1.0` — macro `B`: a linear run of 58 methyl-methacrylate (`MMA`) residues.
  - `C:69:1:LA-0.217,EH-0.493,ST-0.290` — macro `C`: a linear run of 69 residues, each one drawn
    at random as lauryl (`LA`, 21.7%), 2-ethylhexyl (`EH`, 49.3%), or stearyl (`ST`, 29.0%)
    methacrylate — i.e. a random copolymer segment, not a fixed pattern.
- `-seq A B C A` concatenates the macros end-to-end in this order: cap, then the MMA block, then
  the random alkyl-methacrylate block, then a second cap — giving a 1 + 58 + 69 + 1 = 129-residue
  chain overall.
- `-connect` (short for `-connects`) stitches the macros together at specific residues, in the
  form `<seq-index>:<seq-index>:<res_id>-<res_id>` (both indices zero-based). `0:1:0-0` bonds
  macro-position 0 (the first cap, which only has residue 0) to macro-position 1's residue 0 (the
  first MMA); `1:2:57-0` bonds macro-position 1's *last* residue (57, since 58 residues are
  indexed 0–57) to macro-position 2's first; `2:3:68-0` bonds macro-position 2's last residue (68,
  of 69) to the final cap.

### 2. Build the topology

Next, generate the topology with

    polyply gen_params -lib oplsaaLigParGen -o molecule.itp -name PAMA_BLOCK -seqf sequence.json

This reads `sequence.json` and, for each residue, pulls its atoms/bonds/angles/dihedrals from the
`oplsaaLigParGen` library (`-lib`), then adds the inter-residue bonded terms (bonds across the
backbone) wherever `sequence.json` says two residues are connected. The result, `molecule.itp`, is
a complete GROMACS-style topology for one PAMA chain — explicit atoms, explicit bonded parameters,
no further force-field lookups needed for those.

What `gen_params` does *not* supply is the nonbonded (Lennard-Jones) parameters for the PAMA
library's custom OPLS atom types (named `opls_1000` and up, to avoid clashing with the standard
OPLS-AA numbering below 1000) — those live in a separate, shared `custom-ffnonbonded.itp` file
that every chain built from this library needs regardless of its exact sequence.

Place the user-provided `oplsaa.ff` force field directory (the standard one shipped with your
GROMACS installation, e.g. `$GMXDATA/top/oplsaa.ff`) and `custom-ffnonbonded.itp` (the custom
nonbonded parameters mentioned above) in the working directory.

Manually create a `system.top` that pulls all of this together — the standard OPLS-AA defaults
and any plain OPLS-AA atom types used by the chain-end caps (`oplsaa.ff/forcefield.itp`), the
PAMA-specific nonbonded parameters (`custom-ffnonbonded.itp`), and the chain's own topology
(`molecule.itp`), followed by GROMACS's standard `[ system ]`/`[ molecules ]` bookkeeping
declaring one copy of the `PAMA_BLOCK` molecule:

    #include "oplsaa.ff/forcefield.itp"
    #include "custom-ffnonbonded.itp"
    #include "molecule.itp"
    [ system ]
    ; name
    Single PAMA block polymer

    [ molecules ]
    ; name  number
    PAMA_BLOCK 1

### 3. Generate 3D coordinates

Next, generate coordinates with

    polyply gen_coords -p system.top -o default.gro -name PAMA_BLOCK -dens 300

This builds an actual 3D conformation for the chain (a self-avoiding random walk, roughly), sized
to a target mass density of 300 kg/m³ (`-dens`) — deliberately dilute/expanded rather than a
realistic bulk density, since the structure still needs relaxing in the next two steps anyway, and
a loose starting point avoids introducing severe atomic overlaps that energy minimization would
otherwise have to fight through.

### 4. Fix up 1-4 pairs

Note that polyply does not generate 1-4 pairs correctly. In OPLS-AA, atoms separated by exactly
three bonds (a "1-4" pair, e.g. the two end atoms of a dihedral) still interact nonbonded, but with
their Lennard-Jones/Coulomb interactions scaled down (`fudgeLJ`/`fudgeQQ` = 0.5) rather than
excluded outright — GROMACS needs these pairs listed explicitly in a `[ pairs ]` section, and
polyply's output is missing them. Generate all 1-4 pairs from the topology with

    python generate_pairs_from_dihedrals.py -i molecule.itp -o pairs.dat

and insert them into the ITP file with

    python insert_custom_pairs_list.py -p pairs.dat -i molecule.itp -o molecule_with_pairs.itp

`molecule_with_pairs.itp` (not `molecule.itp`) is the file that should be carried forward into
`020_em` and beyond.

### 5. Sanity-check the result

Before spending compute time on a chain that might be wrong, double-check that the charge of the
generated polymer is exactly zero (any residual charge usually means a monomer or cap wasn't
charge-normalized correctly) with

    python check_total_charge.py molecule.itp

Double-check the molecular weight and elemental composition — a quick way to catch, e.g., an
accidentally-doubled residue or a wrong element count — with

    $ python check_molecular_weight.py default.gro 
    Molecular weight: 23390.597 g/mol
    Composition:
       C: 1396
       H: 2540
       O: 254

(As noted in the parent README, these exact numbers depend on the particular random draw from
step 1; re-running `gen_seq` without reusing the committed `sequence.json` will give a chain with
the same length and monomer *ratios* but different numbers here.)
