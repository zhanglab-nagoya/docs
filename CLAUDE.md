# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Sphinx-based notes/documentation collection titled **ZhangLab Docs** (repo: `zhanglab-nagoya/docs`), published to Read the Docs at https://dserver.readthedocs.io. Content is mostly molecular-dynamics workflow notes (GROMACS, LAMMPS, polyply, InterMol) with accompanying input/output sample files, not application code. The underlying Python package is still named `jotelha_docs/` (and `jotelha-docs` in `pyproject.toml`'s `[project] name`) — only the Sphinx project/page title and GitHub URL references were updated after the repo moved to the `zhanglab-nagoya` org; the Python package name was left as-is. The package exists solely to give the Sphinx build a version number via `setuptools_scm`.

## Structure and conventions

- All documentation content lives under `docs/`. Each topic is a directory tree with numeric prefixes (`000_`, `020_`, `030_`, `050_`, ...) that encode step/reading order, e.g. `docs/050_pama/050_single_chain_generation/000_polyply/`.
- **Every content directory has a `README.md`** — this is where the actual prose, commands, and explanations are written. Each directory also has an `index.rst`, but that file is auto-generated boilerplate: it just does `.. include:: README.md` and a `.. toctree::` glob over `*/index`. **Never hand-edit `index.rst` files — edit the `README.md` in that directory instead**, then regenerate the rst stubs (see below).
- Sample/data files (`.itp`, `.gro`, `.mdp`, `.top`, `.lmp`, `.dat`, `.xvg`, helper `.py`/`.sh` scripts) sit alongside each step's `README.md` as concrete artifacts referenced by that step's instructions.
- `docs/distribute_index_rst.py` walks the whole tree and (re)writes an `index.rst` in every non-hidden, non-`_build` directory with the standard include/toctree boilerplate shown above. Run this after adding a new content subdirectory so Sphinx picks it up:
  ```bash
  cd docs && python distribute_index_rst.py
  ```
- `docs/conf.py` injects a title (from the folder name) and a path note into every `index.rst` at build time via Sphinx `source-read` hooks — this is why `index.rst` files themselves stay minimal/generated.
- The root `docs/index.rst` is the one exception that is not regenerated/overwritten the same way — it includes the top-level `README.md` and globs `*/index` directly.

## Building the docs

```bash
pip install -e ".[docs]"      # sphinx, sphinx_rtd_theme, sphinxcontrib-spelling/bibtex, myst-parser
cd docs
make html                      # build; output in docs/_build/html
make spelling                  # spell-check via sphinxcontrib.spelling
```

- Markdown (`README.md`) files are parsed via `myst_parser`.
- Bibliography references use `sphinxcontrib.bibtex` against `docs/refs.bib` (create this file if citations are added; it's referenced by `conf.py` but may not exist yet).
- Read the Docs builds from `.readthedocs.yaml` using `docs/conf.py` as the Sphinx config and installs the package with the `docs` extra.

## Adding new content

1. Create a new numbered directory under the relevant topic path.
2. Write a `README.md` in it with the actual content.
3. Add any accompanying sample files.
4. Run `python docs/distribute_index_rst.py` to generate/refresh `index.rst` stubs across the tree.

## Known environment mismatch: `gmx` vs `gmx_mpi`

`docs/050_pama/050_single_chain_generation/050_conversion/forces/single_point_gmx/README.md` and its `extract_forces.sh` invoke the plain `gmx` binary (`gmx grompp`, `gmx mdrun`, `gmx traj`). On this machine there is no plain `gmx` anywhere — neither the manually installed GROMACS 2026.0 in `~/opt` nor the spack `gromacs` module ship anything but `gmx_mpi`. When actually running that tutorial step here, substitute `gmx_mpi` for `gmx` in both the commands and inside `extract_forces.sh`, or the commands fail with "command not found". This was confirmed by running the full PAMA tutorial pipeline end-to-end (polyply → GROMACS EM/NVT → InterMol conversion → force comparison), which otherwise reproduces the documented results (zero net charge, small GROMACS/LAMMPS energy and force discrepancies). The README/script themselves are left as-is pending a fix.
