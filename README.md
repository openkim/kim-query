# kim-query
![Python package](https://github.com/openkim/kim-query/workflows/Python%20package/badge.svg?branch=master)
[![PyPI](https://img.shields.io/pypi/v/kim-query.svg)](https://pypi.python.org/pypi/kim-query)
[![License](https://img.shields.io/badge/license-CDDL--1.0-blue)](LICENSE.CDDL)

Helper routines for querying the OpenKIM database hosted at https://query.openkim.org


## Usage examples

**LAMMPS**

  ```bash
  kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
  kim_query a0 get_lattice_constant_cubic crystal=["fcc"] species=["Al"] units=["angstrom"]
  ```

**python**

  ```python
  from kim_query import get_lattice_constant_cubic
  get_lattice_constant_cubic(["MO_123629422045_005"], ["fcc"], ["Al"], ["angstrom"])
  ```

**curl**

  ```bash
  curl --data-urlencode 'model=["MO_123629422045_005"]' \
       --data-urlencode 'crystal=["fcc"]'               \
       --data-urlencode 'species=["Al"]'                \
       --data-urlencode 'units=["angstrom"]'            \
       https://query.openkim.org/api/get_lattice_constant_cubic
  ```

## Functions

*Note: For a listing that includes a full parameter list and example usage of
 each function, see
 https://openkim.org/doc/usage/kim-query/*

- **raw\_query** Perform a raw mongo query of the OpenKIM Repository
- **get\_available\_models** Retrieve the latest versions of all models that
  support a given set of atomic species

- **get\_test\_result** Retrieve specific keys from a property instance within
  a result generated by a Test-Model pair

- **get\_lattice\_constant\_cubic** Retrieve the equilibrium lattice constant of
  the conventional unit cell of a cubic crystal comprised of one or more
  species at a given temperature and hydrostatic pressure

- **get\_lattice\_constant\_hexagonal** Retrieve equilibrium lattice constants of
  the conventional unit cell of a hexagonal crystal comprised of one or more
  species at a given temperature and hydrostatic pressure

- **get\_lattice\_constant\_2Dhexagonal** Retrieve equilibrium lattice constant of
  the conventional unit cell of a 2D hexagonal crystal comprised of one or more
  species at a given temperature and hydrostatic pressure

- **get\_cohesive\_energy\_cubic** Retrieve cohesive energy of a cubic crystal
  comprised of one or more species at zero temperature and pressure

- **get\_cohesive\_energy\_hexagonal** Retrieve cohesive energy of a hexagonal
  crystal comprised of one or more species at zero temperature and pressure

- **get\_cohesive\_energy\_2Dhexagonal** Retrieve cohesive energy of a 2D
  hexagonal crystal comprised of one or more species at zero temperature and
  pressure

- **get\_elastic\_constants\_isothermal\_cubic** Retrieve isothermal elastic
  constants of a cubic crystal comprised of one or more species at a given
  temperature and hydrostatic pressure

- **get\_bulk\_modulus\_isothermal\_cubic** Retrieve isothermal bulk modulus of a
  cubic crystal comprised of one or more species at a given temperature and
  hydrostatic pressure

- **get\_bulk\_modulus\_isothermal\_hexagonal** Retrieve isothermal bulk modulus of
  a hexagonal crystal comprised of one or more species at zero temperature and
  pressure

- **get\_linear\_thermal\_expansion\_coefficient\_cubic** Retrieve linear
  coefficient of thermal expansion of a cubic crystal comprised of one or more
  species at a given temperature and hydrostatic pressure, calculated according
  to (change-in-length)/(original-length)/(change-in-temperature)

- **get\_intrinsic\_stacking\_fault\_relaxed\_energy\_fcc** Retrieve relaxed
  intrinsic stacking fault (ISF) energy for a face-centered monoatomic cubic
  crystal at zero temperature and a specified pressure.  The ISF corresponds to
  a fault of the form ABC|BCA.  Relaxation of the atomic coordinates is
  performed in the direction perpendicular to the fault plane

- **get\_extrinsic\_stacking\_fault\_relaxed\_energy\_fcc** Retrieve relaxed
  extrinsic stacking fault (ESF) energy for a face-centered monoatomic cubic
  crystal at zero temperature and a specified pressure.  The ESF corresponds to
  an ABC|BA|BC stacking, which can also be understood as a two-layer twin
  nucleus.  Relaxation of the atomic coordinates is performed in the direction
  perpendicular to the fault plane

- **get\_unstable\_stacking\_fault\_relaxed\_energy\_fcc** Retrieve the relaxed
  unstable stacking fault energy (USFE) of a face-centered monoatomic cubic
  crystal at zero temperature and a specified pressure.  The USFE corresponds to
  the energy barrier for rigidly slipping one-half of an infinite crystal
  relative to the other along a <112> direction (fcc partial dislocation
  direction).  Relaxation of the atomic positions is performed perpendicular to
  the fault plane.

- **get\_unstable\_twinning\_fault\_relaxed\_energy\_fcc** Retrieve the relaxed
  unstable twinning fault energy (UTFE) of a face-centered monoatomic cubic
  crystal at zero temperature and a specified pressure.  The UTFE corresponds
  to the energy barrier for rigidly slipping one part of an infinite crystal on
  a {111} plane adjacent to a preexisting intrinsic stacking fault relative to
  the other part along a <112> direction (fcc partial dislocation direction).
  Relaxation of the atomic coordinates is performed perpendicular to the fault
  plane.

- **get\_surface\_energy\_ideal\_cubic** Retrieve ideal surface energy of a
  high-symmetry surface in a cubic crystal comprised of one or more species at
  zero temperature and pressure, as computed by the latest current version of
  the SurfaceEnergyCubicCrystalBrokenBondFit Test Driver (TD\_955413365818).

- **get\_surface\_energy\_relaxed\_cubic** Retrieve free energy of a cubic relaxed
  surface energy of a high-symmetry surface in a cubic crystal comprised of one
  or more species at a given temperature and hydrostatic pressure.  This
  corresponds to the 'relaxed' surface energy found by performing an energy
  minimization.  At zero temperature, this corresponds to the potential energy
  rather than the free energy.
