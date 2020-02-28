################################################################################
#
#  CDDL HEADER START
#
#  The contents of this file are subject to the terms of the Common Development
#  and Distribution License Version 1.0 (the "License").
#
#  You can obtain a copy of the license at
#  http:# www.opensource.org/licenses/CDDL-1.0.  See the License for the
#  specific language governing permissions and limitations under the License.
#
#  When distributing Covered Code, include this CDDL HEADER in each file and
#  include the License file in a prominent location with the name LICENSE.CDDL.
#  If applicable, add the following below this CDDL HEADER, with the fields
#  enclosed by brackets "[]" replaced with your own identifying information:
#
#  Portions Copyright (c) [yyyy] [name of copyright owner]. All rights reserved.
#
#  CDDL HEADER END
#
#  Copyright (c) 2017-2020, Regents of the University of Minnesota.
#  All rights reserved.
#
#  Contributor(s):
#     Daniel S. Karls
#
################################################################################
r"""Helper routines for querying the OpenKIM database hosted at
https://query.openkim.org.
"""
import requests
import json

__author__ = ["Daniel S. Karls"]
__all__ = [
    "raw_query",
    "get_available_models",
    "get_test_result",
    "get_lattice_constant_cubic",
    "get_lattice_constant_hexagonal",
    "get_lattice_constant_2Dhexagonal",
    "get_cohesive_energy_cubic",
    "get_cohesive_energy_hexagonal",
    "get_cohesive_energy_2Dhexagonal",
    "get_elastic_constants_isothermal_cubic",
    "get_bulk_modulus_isothermal_cubic",
    "get_bulk_modulus_isothermal_hexagonal",
    "get_linear_thermal_expansion_coefficient_cubic",
    "get_intrinsic_stacking_fault_relaxed_energy_fcc",
    "get_extrinsic_stacking_fault_relaxed_energy_fcc",
    "get_unstable_stacking_fault_relaxed_energy_fcc",
    "get_unstable_twinning_fault_relaxed_energy_fcc",
    "get_surface_energy_ideal_cubic",
    "get_surface_energy_relaxed_cubic",
]


def _send_query(params, endpoint):
    # Convert all parameters (which are python objects) to JSON strings
    for param, val in params.items():
        params[param] = json.dumps(val)

    url = "https://query.openkim.org/api"
    if endpoint is not None:
        url = ("/").join((url, endpoint))

    return requests.post(url, data=params).json()


def raw_query(**kwargs):
    """
    Perform a raw mongo query of the OpenKIM Repository

    Usage Examples
    --------------

    python:

      ```
      from kim_query import raw_query
      raw_query(query={'type':'mo', 'species':'Al'}, fields={'kimcode':1},
          database='obj', limit=0, project=["kimcode"])
      ```

    Parameters
    ----------
    query : dict
        Things you want true, expressed as a dictionary of key value pairs,
        e.g. {"type": "td"} makes sure that all objects are test drivers

    fields : dict
        Things you want back, as a dictionary of booleans, e.g.  {"type":1,
        "path":1} returns only the 'type' and 'path' keys in each result

    database : str
        Database you want; valid options are 'obj', 'data', 'job', 'log', and
        'agent'

    sort : str or list
        Keys to sort on, either as a single string or a list with direction,
        e.g.  "kimcode" sorts on kimcode, [["kimcode", -1]] gives reverse
        kimcode

    limit : int
        How many results to return; leave empty or set to 0 to get all results

    skip : int
        How many results you want to skip (generally used only with sorting)

    distinct : str
        A single key whose unique values across the results you want to
        inspect, e.g. "type" would return distinct values of the "type" key
        across the results matching your query criteria.  Note that this
        doesn't play well with other options!

    project : list
        Reduce each result to a list where the elements are given by the order
        of the keys given i.e. ["kimcode", "species"].  Implies flatten.

    flatten : bool
        Whether or not to flatten the keys in the dictionary

    history : bool
        Return full database history. By default, only results with
        "latest"=True are returned.

    count : int
        Return only a count of the number of results returned

    map : str
        A JavaScript function that operates on the map portion of map-reduce.
        For more information, check the MongoDB docs.

    reduce : str
        A JavaScript function that constitutes the reduce part of a map-reduce.
        For more information, check the MongoDB docs.

    Returns
    -------
    List containing the specified fields in each of the documents matching the
    query criteria.  Unless 'project' is used, each matching result document
    will be a dictionary.
    """
    return _send_query(kwargs, None)


def get_available_models(species, model_type=["all"], exclusive=[False]):
    r"""Retrieve the latest versions of all models that support a given set of
    atomic species

    Usage Examples
    --------------

    python:

      ```
      from kim_query import get_available_models
      get_available_models(["Al","Fe"], ["sm"], [True])
      ```

    curl:

      ```
      curl --data-urlencode 'species=["Al","Fe"]' \
           --data-urlencode 'model_type=["sm"]'   \
           --data-urlencode 'exclusive=[true]'    \
           https://query.openkim.org/api/get_available_models
      ```

    Parameters
    ----------
    species : array of double-quoted strings
        The standard chemical symbol(s) of all atomic species that the models
        returned must support, e.g. "Al".

    model_type : array containing one double-quoted string
        Type of the models that are to be returned.  Specifying "mo" will
        cause only Portable Models to be returned, while "sm" will cause only
        Simulator Models to be returned.  If left unspecified, both Portable
        Models and Simulator Models will be returned.  (Default: "all")

    exclusive : array containing one boolean
        Whether models returned must support only the species listed (True), or
        are allowed to support species other than those listed (False).
        (Default: False)

    Returns
    -------
    [models] : array containing zero or more double-quoted strings
        The latest versions of all models of the specified type(s) that support
        all of the atomic species given.
    """
    return _send_query(locals(), "get_available_models")


def get_test_result(test, model, species, prop, keys, units):
    r"""Retrieve specific keys from a property instance within a result
    generated by a Test-Model pair

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query latconst_ecoh split get_test_result &
          test=["LatticeConstantCubicEnergy_fcc_Al__TE_156715955670"] &
          species=["Al"] &
          prop=["cohesive-potential-energy-cubic-crystal"] &
          keys=["a","cohesive-potential-energy"] &
          units=["angstrom","eV"]
      variable a0 equal ${latconst_ecoh_1}
      variable ecoh equal ${latconst_ecoh_2}
      ```

    python:

      ```
      from kim_query import get_test_result
      get_test_result(["TE_156715955670"],
          ["MO_123629422045_005"],
          ["Al"],
          ["cohesive-potential-energy-cubic-crystal"],
          ["a","cohesive-potential-energy"],
          ["angstrom","eV"]
      )
      ```

    curl:

      ```
      curl --data-urlencode 'test=["TE_156715955670"]'                         \
           --data-urlencode 'model=["MO_123629422045_005"]'                    \
           --data-urlencode 'species=["Al"]'                                   \
           --data-urlencode 'prop=["cohesive-potential-energy-cubic-crystal"]' \
           --data-urlencode 'keys=["a","cohesive-potential-energy"]'           \
           --data-urlencode 'units=["angstrom","eV"]'                          \
           https://query.openkim.org/api/get_test_result
      ```

    Parameters
    ----------
    test : array containing one double-quoted string
        The KIM ID of the test used to compute the test result

    model : array containing one double-quoted string
        The KIM ID of the model used to compute the test result

    species : array of double-quoted strings
        The standard chemical symbol(s) reported in the 'species' key of the
        test result.  Each symbol listed, and no others, must be present.

    prop : array containing one double-quoted string
        The name of the property definition reported in the test result

    keys : array of double-quoted strings
        The keys of the property definition given in 'prop' that are to be
        returned

    units : array of double-quoted strings
        The units in which each key in 'keys' is to be returned.  Each string
        must correspond to a set of units recognized by [GNU
        units](https://www.gnu.org/software/units/).  The special string "SI"
        (case-insensitive) may also be used if standard SI units are desired
        for a given key.  Keys which are intrinsically unitless, i.e. those
        which have 'has-units = False' in their property definition, must have
        the value 'null' (without quotes) specified.

    Returns
    -------
    An array containing the values of each key listed in 'keys' in the units
    specified by 'units'.  If no matching results are found, an empty list is
    returned.
    """
    return _send_query(locals(), "get_test_result")


def get_lattice_constant_cubic(
    model,
    crystal,
    species,
    units,
    temperature=[0.0],
    temperature_units=["K"],
    temperature_tol=[0.1],
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["relaxation"],
):
    r"""Retrieve the equilibrium lattice constant of the conventional unit cell
    of a cubic crystal comprised of one or more species at a given temperature
    and hydrostatic pressure

    KIM Property Definition: [structure-cubic-crystal-npt](https://openkim.org/properties/show/2014-04-15/staff@noreply.openkim.org/structure-cubic-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query a0 get_lattice_constant_cubic crystal=["fcc"] species=["Al"] units=["angstrom"]
      ```

    python:

      ```
      from kim_query import get_lattice_constant_cubic
      get_lattice_constant_cubic(["MO_123629422045_005"], ["fcc"], ["Al"], ["angstrom"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_123629422045_005"]' \
           --data-urlencode 'crystal=["fcc"]'               \
           --data-urlencode 'species=["Al"]'                \
           --data-urlencode 'units=["angstrom"]'            \
           https://query.openkim.org/api/get_lattice_constant_cubic
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the cubic crystal.  Currently allowed values are
        "bcc", "diamond", "fcc", and "sc".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of length supported by [GNU units](https://www.gnu.org/software/units/)
        in which the lattice constant will be returned, e.g. "angstrom".

    temperature : array containing one float, optional
        The temperature at which the equilibrium lattice geometry is computed.
        This value should be given in the units specified by the
        'temperature_units' argument.  (Default: 0.0)

    temperature_units : array containing one double-quoted string, optional
        A physical unit of temperature supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'temperature' argument is given.  (Default: K)

    temperature_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        temperature specified in the given temperature units.  For example, if
        temperature_tol=0.1, temperature=293.15, temperature_units="K", then
        results retrieved by the query must be computed at a temperature of
        293.15 +/- 0.1 K.  If multiple matching results are found, an error is
        returned.  (Default: 0.1)

    pressure : array containing one float, optional
        The pressure at which the equilibrium lattice geometry is
        computed.  This value should be given in the units specified by the
        'pressure_units' argument.  (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple matching results are found, an error is returned.
        (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to compute the lattice constant.  Currently allowed
        values are:

      |-----------------------------------+------------------------------------------------------|
      | Allowed values                    | Description                                          |
      |-----------------------------------|------------------------------------------------------|
      | "TD_475411767977" \| "relaxation" | Nelder-Mead downhill simplex minimization. (default) |
      |-----------------------------------+------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [a] : array containing one float
        The lattice constant of the conventional unit cell of the cubic crystal
        in the requested units.

    """
    return _send_query(locals(), "get_lattice_constant_cubic")


def get_lattice_constant_hexagonal(
    model,
    crystal,
    species,
    units,
    temperature=[0.0],
    temperature_units=["K"],
    temperature_tol=[0.1],
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["relaxation"],
):
    r"""Retrieve equilibrium lattice constants of the conventional unit cell of
    a hexagonal crystal comprised of one or more species at a given temperature
    and hydrostatic pressure

    KIM Property Definition: [structure-hexagonal-crystal-npt](https://openkim.org/properties/show/2014-04-15/staff@noreply.openkim.org/structure-hexagonal-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_Mendelev_2007_Zr__MO_848899341753_000 metal
      kim_query latconst split get_lattice_constant_hexagonal crystal=["hcp"] species=["Zr"] units=["angstrom"]
      ```

    python:

      ```
      from kim_query import get_lattice_constant_hexagonal
      get_lattice_constant_hexagonal(["MO_848899341753_000"], ["hcp"], ["Zr"], ["angstrom"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_848899341753_000"]' \
           --data-urlencode 'crystal=["hcp"]'               \
           --data-urlencode 'species=["Zr"]'                \
           --data-urlencode 'units=["angstrom"]'            \
           https://query.openkim.org/api/get_lattice_constant_hexagonal
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the hexagonal crystal.  Currently allowed values are
        "graphite", "hcp", and "sh".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of length supported by [GNU units](https://www.gnu.org/software/units/)
        in which the lattice constants will be returned, e.g. "angstrom".

    temperature : array containing one float, optional
        The temperature at which the equilibrium lattice geometry is computed.
        This value should be given in the units specified by the
        'temperature_units' argument.  (Default: 0.0)

    temperature_units : array containing one double-quoted string, optional
        A physical unit of temperature supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'temperature' argument is given.  (Default: K)

    temperature_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        temperature specified in the given temperature units.  For example, if
        temperature_tol=0.1, temperature=293.15, temperature_units="K", then
        results retrieved by the query must be computed at a temperature of
        293.15 +/- 0.1 K.  If multiple matching results are found, an error is
        returned.  (Default: 0.1)

    pressure : array containing one float, optional
        The pressure at which the equilibrium lattice geometry is
        computed.  This value should be given in the units specified by the
        'pressure_units' argument.  (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple matching results are found, an error is returned.
        (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to compute the lattice constants.  Currently allowed
        values are:

      |-----------------------------------+------------------------------------------------------|
      | Allowed values                    | Description                                          |
      |-----------------------------------|------------------------------------------------------|
      | "TD_942334626465" \| "relaxation" | Nelder-Mead downhill simplex minimization. (default) |
      |-----------------------------------+------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [a, c] : array containing two floats
        The lattice constants of the conventional unit cell of the hexagonal
        crystal in the requested units.

    """
    return _send_query(locals(), "get_lattice_constant_hexagonal")


def get_lattice_constant_2Dhexagonal(
    model,
    crystal,
    species,
    units,
    temperature=[0.0],
    temperature_units=["K"],
    temperature_tol=[0.1],
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["relaxation"],
):
    r"""Retrieve equilibrium lattice constant of the conventional unit cell of
    a 2D hexagonal crystal comprised of one or more species at a given
    temperature and hydrostatic pressure

    KIM Property Definition: [structure-2d-hexagonal-crystal-npt](https://openkim.org/properties/show/2015-05-26/staff@noreply.openkim.org/structure-2d-hexagonal-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init Tersoff_LAMMPS_Tersoff_1988_C__MO_579868029681_002 metal
      kim_query a0 get_lattice_constant_2Dhexagonal crystal=["graphene-like"] species=["C"] units=["angstrom"]
      ```

    python:

      ```
      from kim_query import get_lattice_constant_2Dhexagonal
      get_lattice_constant_2Dhexagonal(["MO_579868029681_002"], ["graphene-like"], ["C"], ["angstrom"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_579868029681_002"]' \
           --data-urlencode 'crystal=["graphene-like"]'     \
           --data-urlencode 'species=["C"]'                 \
           --data-urlencode 'units=["angstrom"]'            \
           https://query.openkim.org/api/get_lattice_constant_2Dhexagonal
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the 2D hexagonal crystal.  Currently, a single value
        is allowed:  "graphene-like".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the 2D
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of length supported by [GNU units](https://www.gnu.org/software/units/)
        in which the lattice constant will be returned, e.g. "angstrom".

    temperature : array containing one float, optional
        The temperature at which the equilibrium lattice geometry is computed.
        This value should be given in the units specified by the
        'temperature_units' argument.  (Default: 0.0)

    temperature_units : array containing one double-quoted string, optional
        A physical unit of temperature supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'temperature' argument is given.  (Default: K)

    temperature_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        temperature specified in the given temperature units.  For example, if
        temperature_tol=0.1, temperature=293.15, temperature_units="K", then
        results retrieved by the query must be computed at a temperature of
        293.15 +/- 0.1 K.  If multiple matching results are found, an error is
        returned.  (Default: 0.1)

    pressure : array containing one float, optional
        The pressure at which the equilibrium lattice geometry is
        computed.  This value should be given in the units specified by the
        'pressure_units' argument.  (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple matching results are found, an error is returned.
        (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to compute the lattice constant.  Currently allowed
        values are:

      |-----------------------------------+----------------------------------------------------------|
      | Allowed values                    | Description                                              |
      |-----------------------------------|----------------------------------------------------------|
      | "TD_034540307932" \| "relaxation" | Polak-Ribiere conjugate gradient minimization. (default) |
      |-----------------------------------+----------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [a] : array containing one float
        The lattice constant of the conventional unit cell of the 2D hexagonal
        crystal in the requested units.

    """
    return _send_query(locals(), "get_lattice_constant_2Dhexagonal")


def get_cohesive_energy_cubic(model, crystal, species, units, method=["relaxation"]):
    r"""Retrieve cohesive energy of a cubic crystal comprised of one or more
    species at zero temperature and pressure

    KIM Property Definition: [cohesive-potential-energy-cubic-crystal](https://openkim.org/properties/show/2014-04-15/staff@noreply.openkim.org/cohesive-potential-energy-cubic-crystal)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query Ec get_cohesive_energy_cubic crystal=["fcc"] species=["Al"] units=["eV"]
      ```

    python:

      ```
      from kim_query import get_cohesive_energy_cubic
      get_cohesive_energy_cubic(["MO_123629422045_005"], ["fcc"], ["Al"], ["eV"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_123629422045_005"]' \
           --data-urlencode 'crystal=["fcc"]'               \
           --data-urlencode 'species=["Al"]'                \
           --data-urlencode 'units=["eV"]'                  \
           https://query.openkim.org/api/get_cohesive_energy_cubic
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the cubic crystal.  Currently allowed values are
        "bcc", "diamond", "fcc", and "sc".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of energy supported by [GNU units](https://www.gnu.org/software/units/)
        in which the cohesive energy will be returned, e.g. "eV".

    method : array containing one double-quoted string, optional
        The algorithm used to compute the cohesive energy.  Currently allowed
        values are:

      |-----------------------------------+------------------------------------------------------|
      | Allowed values                    | Description                                          |
      |-----------------------------------|------------------------------------------------------|
      | "TD_475411767977" \| "relaxation" | Nelder-Mead downhill simplex minimization. (default) |
      |-----------------------------------+------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [cohesive_energy] : array containing one float
        The cohesive energy in the requested units.  This is the IUPAC definition,
        i.e. a stable crystal will have a *positive* cohesive energy.

    """
    return _send_query(locals(), "get_cohesive_energy_cubic")


def get_cohesive_energy_hexagonal(
    model, crystal, species, units, method=["relaxation"]
):
    r"""Retrieve cohesive energy of a hexagonal crystal comprised of one or
    more species at zero temperature and pressure

    KIM Property Definition: [cohesive-potential-energy-hexagonal-crystal](https://openkim.org/properties/show/2014-04-15/staff@noreply.openkim.org/cohesive-potential-energy-hexagonal-crystal)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_Mendelev_2007_Zr__MO_848899341753_000 metal
      kim_query Ec get_cohesive_energy_hexagonal crystal=["hcp"] species=["Zr"] units=["eV"]
      ```

    python:

      ```
      from kim_query import get_cohesive_energy_hexagonal
      get_cohesive_energy_hexagonal(["MO_848899341753_000"], ["hcp"], ["Zr"], ["eV"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_848899341753_000"]' \
           --data-urlencode 'crystal=["hcp"]'               \
           --data-urlencode 'species=["Zr"]'                \
           --data-urlencode 'units=["eV"]'                  \
           https://query.openkim.org/api/get_cohesive_energy_hexagonal
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the hexagonal crystal.  Currently allowed values are
        "graphite", "hcp", and "sh".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of energy supported by [GNU units](https://www.gnu.org/software/units/)
        in which the cohesive energy will be returned, e.g. "eV".

    method : array containing one double-quoted string, optional
        The algorithm used to compute the cohesive energy.  Currently allowed
        values are:

      |-----------------------------------+------------------------------------------------------|
      | Allowed values                    | Description                                          |
      |-----------------------------------|------------------------------------------------------|
      | "TD_942334626465" \| "relaxation" | Nelder-Mead downhill simplex minimization. (default) |
      |-----------------------------------+------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [cohesive_energy] : array containing one float
        The cohesive energy in the requested units.  This is the IUPAC definition,
        i.e. a stable crystal will have a *positive* cohesive energy.

    """
    # NOTE: This currently won't ever return any results because the current version of
    # the LatticeConstantHexagonal driver only reports
    # 'cohesive-free-energy-hexagonal-crystal' and 'structure-hexagonal-crystal-npt'
    return _send_query(locals(), "get_cohesive_energy_hexagonal")


def get_cohesive_energy_2Dhexagonal(
    model, crystal, species, units, method=["relaxation"]
):
    r"""Retrieve cohesive energy of a 2D hexagonal crystal comprised of one or
    more species at zero temperature and pressure

    KIM Property Definition: [cohesive-potential-energy-2d-hexagonal-crystal](https://openkim.org/properties/show/2015-05-26/staff@noreply.openkim.org/cohesive-potential-energy-2d-hexagonal-crystal)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init Tersoff_LAMMPS_Tersoff_1988_C__MO_579868029681_002 metal
      kim_query Ec get_cohesive_energy_2Dhexagonal crystal=["graphene-like"] species=["C"] units=["eV"]
      ```

    python:

      ```
      from kim_query import get_cohesive_energy_2Dhexagonal
      get_cohesive_energy_2Dhexagonal(["MO_579868029681_002"], ["graphene-like"], ["C"], ["eV"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_579868029681_002"]' \
           --data-urlencode 'crystal=["graphene-like"]'     \
           --data-urlencode 'species=["C"]'                 \
           --data-urlencode 'units=["eV"]'                  \
           https://query.openkim.org/api/get_cohesive_energy_2Dhexagonal
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the hexagonal crystal.  Currently, only a single
        value is allowed:  "graphene-like".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of energy supported by [GNU units](https://www.gnu.org/software/units/)
        in which the cohesive energy will be returned, e.g. "eV".

    method : array containing one double-quoted string, optional
        The algorithm used to compute the cohesive energy.  Currently allowed
        values are:

      |-----------------------------------+----------------------------------------------------------|
      | Allowed values                    | Description                                              |
      |-----------------------------------|----------------------------------------------------------|
      | "TD_034540307932" \| "relaxation" | Polak-Ribiere conjugate gradient minimization. (default) |
      |-----------------------------------+----------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [cohesive_energy] : array containing one float
        The cohesive energy in the requested units.  This is the IUPAC definition,
        i.e. a stable crystal will have a *positive* cohesive energy.

    """
    return _send_query(locals(), "get_cohesive_energy_2Dhexagonal")


def get_elastic_constants_isothermal_cubic(
    model,
    crystal,
    species,
    units,
    temperature=[0.0],
    temperature_units=["K"],
    temperature_tol=[0.1],
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["finite-difference"],
):
    r"""Retrieve isothermal elastic constants of a cubic crystal comprised of
    one or more species at a given temperature and hydrostatic pressure

    KIM Property Definition: [elastic-constants-isothermal-cubic-crystal-npt](https://openkim.org/properties/show/2014-05-21/staff@noreply.openkim.org/elastic-constants-isothermal-cubic-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query elastconst split get_elastic_constants_isothermal_cubic crystal=["fcc"] species=["Al"] units=["GPa"]
      ```

    python:

      ```
      from kim_query import get_elastic_constants_isothermal_cubic
      get_elastic_constants_isothermal_cubic(["MO_123629422045_005"], ["fcc"], ["Al"], ["GPa"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_123629422045_005"]' \
           --data-urlencode 'crystal=["fcc"]'               \
           --data-urlencode 'species=["Al"]'                \
           --data-urlencode 'units=["GPa"]'                 \
           https://query.openkim.org/api/get_elastic_constants_isothermal_cubic
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the cubic crystal.  Currently allowed values are
        "bcc", "diamond", "fcc", and "sc".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the elastic constants will be returned, e.g. "GPa".

    temperature : array containing one float, optional
        The temperature at which the equilibrium elastic constants are
        computed.  This value should be given in the units specified by the
        'temperature_units' argument.  (Default: 0.0)

    temperature_units : array containing one double-quoted string, optional
        A physical unit of temperature supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'temperature' argument is given.  (Default: K)

    temperature_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        temperature specified in the given temperature units.  For example, if
        temperature_tol=0.1, temperature=293.15, temperature_units="K", then
        results retrieved by the query must be computed at a temperature of
        293.15 +/- 0.1 K.  If multiple matching results are found, an error is
        returned.  (Default: 0.1)

    pressure : array containing one float, optional
        The pressure at which the elastic constants are computed.
        This value should be given in the units specified by the
        'pressure_units' argument.  (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple results are found which match the specified
        pressure within this tolerance, an error is returned.  (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to compute the elastic constants.  Currently allowed
        values are:

      |------------------------------------------+-----------------------------------------------------------------------------------|
      | Allowed values                           | Description                                                                       |
      |------------------------------------------|-----------------------------------------------------------------------------------|
      | "TD_011862047401" \| "finite-difference" | Second-order central finite differences and Richardson extrapolation used to approximate the Hessian of the energy. (default) |
      |------------------------------------------+-----------------------------------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [c11, c12, c44] : array containing three floats
        The isothermal cubic elastic constants in the requested units.

    """
    return _send_query(locals(), "get_elastic_constants_isothermal_cubic")


def get_bulk_modulus_isothermal_cubic(
    model,
    crystal,
    species,
    units,
    temperature=[0.0],
    temperature_units=["K"],
    temperature_tol=[0.1],
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["finite-difference"],
):
    r"""Retrieve isothermal bulk modulus of a cubic crystal comprised of one or
    more species at a given temperature and hydrostatic pressure

    KIM Property Definition: [bulk-modulus-isothermal-cubic-crystal-npt](https://openkim.org/properties/show/2014-04-15/staff@noreply.openkim.org/bulk-modulus-isothermal-cubic-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query B get_bulk_modulus_isothermal_cubic crystal=["fcc"] species=["Al"] units=["GPa"]
      ```

    python:

      ```
      from kim_query import get_bulk_modulus_isothermal_cubic
      get_bulk_modulus_isothermal_cubic(["MO_123629422045_005"], ["fcc"], ["Al"], ["GPa"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_123629422045_005"]' \
           --data-urlencode 'crystal=["fcc"]'               \
           --data-urlencode 'species=["Al"]'                \
           --data-urlencode 'units=["GPa"]'                 \
           https://query.openkim.org/api/get_bulk_modulus_isothermal_cubic
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the cubic crystal.  Currently allowed values are
        "bcc", "diamond", "fcc", and "sc".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the bulk modulus will be returned, e.g. "GPa".

    temperature : array containing one float, optional
        The temperature at which the bulk modulus is computed.  This value
        should be given in the units specified by the 'temperature_units'
        argument.  (Default: 0.0)

    temperature_units : array containing one double-quoted string, optional
        A physical unit of temperature supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'temperature' argument is given.  (Default: K)

    temperature_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        temperature specified in the given temperature units.  For example, if
        temperature_tol=0.1, temperature=293.15, temperature_units="K", then
        results retrieved by the query must be computed at a temperature of
        293.15 +/- 0.1 K.  If multiple matching results are found, an error is
        returned.  (Default: 0.1)

    pressure : array containing one float, optional
        The pressure at which the bulk modulus is computed.  This value should
        be given in the units specified by the 'pressure_units' argument.
        (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple matching results are found, an error is returned.
        (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to compute the isothermal bulk modulus.  Currently
        allowed values are:

      |------------------------------------------+-----------------------------------------------------------------------------------|
      | Allowed values                           | Description                                                                       |
      |------------------------------------------|-----------------------------------------------------------------------------------|
      | "TD_011862047401" \| "finite-difference" | Second-order central finite differences and Richardson extrapolation used to approximate the Hessian of the energy. (default) |
      |------------------------------------------+-----------------------------------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [B] : array containing one float
        The isothermal bulk modulus in the requested units.

    """
    return _send_query(locals(), "get_bulk_modulus_isothermal_cubic")


def get_bulk_modulus_isothermal_hexagonal(
    model,
    crystal,
    species,
    units,
    temperature=[0.0],
    temperature_units=["K"],
    temperature_tol=[0.1],
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["finite-difference"],
):
    r"""Retrieve isothermal bulk modulus of a hexagonal crystal comprised of
    one or more species at zero temperature and pressure

    KIM Property Definition: [bulk-modulus-isothermal-hexagonal-crystal-npt](https://openkim.org/properties/show/2014-04-15/staff@noreply.openkim.org/bulk-modulus-isothermal-hexagonal-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_Mendelev_2007_Zr__MO_848899341753_000 metal
      kim_query B get_bulk_modulus_isothermal_hexagonal crystal=["hcp"] species=["Zr"] units=["GPa"]
      ```

    python:

      ```
      from kim_query import get_bulk_modulus_isothermal_hexagonal
      get_bulk_modulus_isothermal_hexagonal(["MO_848899341753_000"], ["hcp"], ["Zr"], ["GPa"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_848899341753_000"]' \
           --data-urlencode 'crystal=["hcp"]'               \
           --data-urlencode 'species=["Zr"]'                \
           --data-urlencode 'units=["GPa"]'                 \
           https://query.openkim.org/api/get_bulk_modulus_isothermal_hexagonal
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the hexagonal crystal.  Currently allowed values are
        "graphite", "hcp", and "sh".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the bulk modulus will be returned, e.g. "GPa".

    temperature : array containing one float, optional
        The temperature at which the bulk modulus is computed.  This value
        should be given in the units specified by the 'temperature_units'
        argument.  (Default: 0.0)

    temperature_units : array containing one double-quoted string, optional
        A physical unit of temperature supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'temperature' argument is given.  (Default: K)

    temperature_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        temperature specified in the given temperature units.  For example, if
        temperature_tol=0.1, temperature=293.15, temperature_units="K", then
        results retrieved by the query must be computed at a temperature of
        293.15 +/- 0.1 K.  If multiple matching results are found, an error is
        returned.  (Default: 0.1)

    pressure : array containing one float, optional
        The pressure at which the bulk modulus is computed.  This value should
        be given in the units specified by the 'pressure_units' argument.
        (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match
        the pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple matching results are found, an error is returned.
        (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to compute the isothermal bulk modulus.  Currently
        allowed values are:

      |------------------------------------------+-----------------------------------------------------------------------------------|
      | Allowed values                           | Description                                                                       |
      |------------------------------------------|-----------------------------------------------------------------------------------|
      | "TD_612503193866" \| "finite-difference" | Second-order central finite differences and Richardson extrapolation used to approximate the Hessian of the energy. (default) |
      |------------------------------------------+-----------------------------------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [B] : array containing one float
        The isothermal bulk modulus in the requested units.

    """
    return _send_query(locals(), "get_bulk_modulus_isothermal_hexagonal")


def get_linear_thermal_expansion_coefficient_cubic(
    model,
    crystal,
    species,
    units,
    temperature=[0.0],
    temperature_units=["K"],
    temperature_tol=[0.1],
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["md-volume-expansion"],
):
    r"""Retrieve linear coefficient of thermal expansion of a cubic crystal
    comprised of one or more species at a given temperature and hydrostatic pressure,
    calculated according to (change-in-length)/(original-length)/(change-in-temperature)

    KIM Property Definition: [linear-thermal-expansion-coefficient-cubic-crystal-npt](https://openkim.org/properties/show/2015-07-30/staff@noreply.openkim.org/linear-thermal-expansion-coefficient-cubic-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query alpha get_linear_thermal_expansion_coefficient_cubic crystal=["fcc"] species=["Al"] units=["1/K"] temperature=[293.15] temperature_units=["K"]
      ```

    python:

      ```
      from kim_query import get_linear_thermal_expansion_coefficient_cubic
      get_linear_thermal_expansion_coefficient_cubic(["MO_123629422045_005"], ["fcc"], ["Al"], ["1/K"], [293.15])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_123629422045_005"]' \
           --data-urlencode 'crystal=["fcc"]'               \
           --data-urlencode 'species=["Al"]'                \
           --data-urlencode 'units=["1/K"]'                 \
           --data-urlencode 'temperature=[293.15]'          \
           https://query.openkim.org/api/get_linear_thermal_expansion_coefficient_cubic
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the cubic crystal.  Currently allowed values are
        "bcc", "diamond", "fcc", and "sc".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of 1/temperature supported by [GNU units](https://www.gnu.org/software/units/)
        in which the bulk modulus will be returned, e.g. "1/K".

    temperature : array containing one float, optional
        The temperature at which the linear thermal expansion coefficient is to
        be computed.  This value should be given in the units specified
        by the 'temperature_units' argument.  (Default: 293.15)

    temperature_units : array containing one double-quoted string, optional
        A physical unit of temperature supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'temperature' argument is given.  (Default: K)

    temperature_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        temperature specified in the given temperature units.  For example, if
        temperature_tol=0.1, temperature=293.15, temperature_units="K", then
        results retrieved by the query must be computed at a temperature of
        293.15 +/- 0.1 K.  If multiple matching results are found, an error is
        returned.  (Default: 0.1)

    pressure : array containing one float, optional
        The pressure at which the linear thermal expansion coefficient is to
        be computed.  This value should be given in the units specified
        by the 'pressure_units' argument.  (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple matching results are found, an error is returned.
        (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to compute the linear thermal expansion coefficient.
        Currently allowed values are:

      |--------------------------------------------+-----------------------------------------------------------------------------------|
      | Allowed values                             | Description                                                                       |
      |--------------------------------------------|-----------------------------------------------------------------------------------|
      | "TD_522633393614" \| "md-volume-expansion" | Time integration performed under npt ensemble using a Nose-Hoover thermostat and barostate at a range of temperatures while allowing the system volume to change, recording the average volume once the temperature and pressure have converged. (default)
      |--------------------------------------------+-----------------------------------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [alpha] : array containing one float
        The linear thermal expansion coefficient in the requested units.

    """
    return _send_query(locals(), "get_linear_thermal_expansion_coefficient_cubic")


def get_intrinsic_stacking_fault_relaxed_energy_fcc(
    model,
    species,
    units,
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["relaxation"],
):
    r"""Retrieve relaxed intrinsic stacking fault (ISF) energy for a
    face-centered monoatomic cubic crystal at zero temperature and a specified
    pressure.  The ISF corresponds to a fault of the form ABC|BCA.  Relaxation
    of the atomic coordinates is performed in the direction perpendicular to
    the fault plane

    KIM Property Definition: [intrinsic-stacking-fault-relaxed-energy-fcc-crystal-npt](https://openkim.org/properties/show/2015-05-26/staff@noreply.openkim.org/intrinsic-stacking-fault-relaxed-energy-fcc-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query Estack_intr get_intrinsic_stacking_fault_relaxed_energy_fcc species=["Al"] units=["eV/angstrom^2"]
      ```

    python:

      ```
      from kim_query import get_intrinsic_stacking_fault_relaxed_energy_fcc
      get_intrinsic_stacking_fault_relaxed_energy_fcc(["MO_123629422045_005"], ["Al"], ["eV/angstrom^2"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_123629422045_005"]' \
           --data-urlencode 'species=["Al"]'                \
           --data-urlencode 'units=["eV/angstrom^2"]'       \
           https://query.openkim.org/api/get_intrinsic_stacking_fault_relaxed_energy_fcc
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    species : array containing one string
        The standard chemical symbol of the single atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of energy per unit area supported by [GNU units](https://www.gnu.org/software/units/)
        in which the relaxed intrinsic stacking fault energy will be returned,
        e.g. "eV/angstrom^2".

    pressure : array containing one float, optional
        The pressure at which the relaxed stacking fault energy is
        computed.  This value should be given in the units specified by the
        'pressure_units' argument.  (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple matching results are found, an error is returned.
        (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to relax the atomic positions in order to compute
        the relaxed intrinsic stacking fault energy for a given lattice
        constant.  Currently allowed values are:

      |-----------------------------------+----------------------------------------------------------|
      | Allowed values                    | Description                                              |
      |-----------------------------------|----------------------------------------------------------|
      | "TD_228501831190" \| "relaxation" | Polak-Ribiere conjugate gradient minimization. (default) |
      |-----------------------------------+----------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [intrinsic_stacking_fault_energy] : array containing one float
        The relaxed intrinsic stacking fault energy of the monoatomic FCC
        crystal in the requested units.

    """
    return _send_query(locals(), "get_intrinsic_stacking_fault_relaxed_energy_fcc")


def get_extrinsic_stacking_fault_relaxed_energy_fcc(
    model,
    species,
    units,
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["relaxation"],
):
    r"""Retrieve relaxed extrinsic stacking fault (ESF) energy for a
    face-centered monoatomic cubic crystal at zero temperature and a specified
    pressure.  The ESF corresponds to an ABC|BA|BC stacking, which can also be
    understood as a two-layer twin nucleus.  Relaxation of the atomic
    coordinates is performed in the direction perpendicular to the fault plane

    KIM Property Definition: [extrinsic-stacking-fault-relaxed-energy-fcc-crystal-npt](https://openkim.org/properties/show/2015-05-26/staff@noreply.openkim.org/extrinsic-stacking-fault-relaxed-energy-fcc-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query Estack_extr get_extrinsic_stacking_fault_relaxed_energy_fcc species=["Al"] units=["eV/angstrom^2"]
      ```

    python:

      ```
      from kim_query import get_extrinsic_stacking_fault_relaxed_energy_fcc
      get_extrinsic_stacking_fault_relaxed_energy_fcc(["MO_123629422045_005"], ["Al"], ["eV/angstrom^2"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_123629422045_005"]' \
           --data-urlencode 'species=["Al"]'                \
           --data-urlencode 'units=["eV/angstrom^2"]'       \
           https://query.openkim.org/api/get_extrinsic_stacking_fault_relaxed_energy_fcc
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    species : array containing one string
        The standard chemical symbol of the single atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of energy per unit area supported by [GNU units](https://www.gnu.org/software/units/)
        in which the relaxed intrinsic stacking fault energy will be returned,
        e.g. "eV/angstrom^2".

    pressure : array containing one float, optional
        The pressure at which the relaxed stacking fault energy is
        computed.  This value should be given in the units specified by the
        'pressure_units' argument.  (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple matching results are found, an error is returned.
        (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to relax the atomic positions in order to compute
        the relaxed extrinsic stacking fault energy for a given lattice
        constant.  Currently allowed values are:

      |-----------------------------------+----------------------------------------------------------|
      | Allowed values                    | Description                                              |
      |-----------------------------------|----------------------------------------------------------|
      | "TD_228501831190" \| "relaxation" | Polak-Ribiere conjugate gradient minimization. (default) |
      |-----------------------------------+----------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [extrinsic_stacking_fault_energy] : array containing one float
        The relaxed extrinsic stacking fault energy of the monoatomic FCC
        crystal in the requested units.

    """
    return _send_query(locals(), "get_extrinsic_stacking_fault_relaxed_energy_fcc")


def get_unstable_stacking_fault_relaxed_energy_fcc(
    model,
    species,
    units,
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["relaxation"],
):
    r"""Retrieve the relaxed unstable stacking fault energy (USFE) of a
    face-centered monoatomic cubic crystal at zero temperature and a specified
    pressure.  The USFE corresponds to the energy barrier for rigidly slipping
    one-half of an infinite crystal relative to the other along a <112>
    direction (fcc partial dislocation direction).  Relaxation of the atomic
    positions is performed perpendicular to the fault plane.

    KIM Property Definition: [unstable-stacking-fault-relaxed-energy-fcc-crystal-npt](https://openkim.org/properties/show/2015-05-26/staff@noreply.openkim.org/unstable-stacking-fault-relaxed-energy-fcc-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query Estack_unstable get_unstable_stacking_fault_relaxed_energy_fcc species=["Al"] units=["eV/angstrom^2"]
      ```

    python:

      ```
      from kim_query import get_unstable_stacking_fault_relaxed_energy_fcc
      get_unstable_stacking_fault_relaxed_energy_fcc(["MO_123629422045_005"], ["Al"], ["eV/angstrom^2"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_123629422045_005"]' \
           --data-urlencode 'species=["Al"]'                \
           --data-urlencode 'units=["eV/angstrom^2"]'       \
           https://query.openkim.org/api/get_unstable_stacking_fault_relaxed_energy_fcc
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    species : array containing one string
        The standard chemical symbol of the single atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of energy per unit area supported by [GNU units](https://www.gnu.org/software/units/)
        in which the relaxed intrinsic stacking fault energy will be returned,
        e.g. "eV/angstrom^2".

    pressure : array containing one float, optional
        The pressure at which the relaxed unstable stacking fault energy is to
        be computed.  This value should be given in the units specified
        by the 'pressure_units' argument.  (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple matching results are found, an error is returned.
        (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to relax the atomic positions in order to compute
        the unstable stacking fault energy for a given lattice constant.
        Currently allowed values are:

      |-----------------------------------+----------------------------------------------------------|
      | Allowed values                    | Description                                              |
      |-----------------------------------|----------------------------------------------------------|
      | "TD_228501831190" \| "relaxation" | Polak-Ribiere conjugate gradient minimization. (default) |
      |-----------------------------------+----------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [unstable_stacking_fault_energy] : array containing one float
        The relaxed unstable stacking fault energy of the monoatomic FCC
        crystal in the requested units.

    """
    return _send_query(locals(), "get_unstable_stacking_fault_relaxed_energy_fcc")


def get_unstable_twinning_fault_relaxed_energy_fcc(
    model,
    species,
    units,
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["relaxation"],
):
    r"""Retrieve the relaxed unstable twinning fault energy (UTFE) of a
    face-centered monoatomic cubic crystal at zero temperature and a specified
    pressure.  The UTFE corresponds to the energy barrier for rigidly slipping
    one part of an infinite crystal on a {111} plane adjacent to a preexisting
    intrinsic stacking fault relative to the other part along a <112> direction
    (fcc partial dislocation direction).  Relaxation of the atomic coordinates
    is performed perpendicular to the fault plane.

    KIM Property Definition: [unstable-twinning-fault-relaxed-energy-fcc-crystal-npt](https://openkim.org/properties/show/2015-05-26/staff@noreply.openkim.org/unstable-twinning-fault-relaxed-energy-fcc-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query Etwin_unstable get_unstable_twinning_fault_relaxed_energy_fcc species=["Al"] units=["eV/angstrom^2"]
      ```

    python:

      ```
      from kim_query import get_unstable_twinning_fault_relaxed_energy_fcc
      get_unstable_twinning_fault_relaxed_energy_fcc(["MO_123629422045_005"], ["Al"], ["eV/angstrom^2"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_123629422045_005"]' \
           --data-urlencode 'species=["Al"]'                \
           --data-urlencode 'units=["eV/angstrom^2"]'       \
           https://query.openkim.org/api/get_unstable_twinning_fault_relaxed_energy_fcc
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    species : array containing one string
        The standard chemical symbol of the single atomic species comprising the
        crystal, e.g. "Al".

    units : array containing one double-quoted string
        A physical unit of energy per unit area supported by [GNU units](https://www.gnu.org/software/units/)
        in which the relaxed intrinsic stacking fault energy will be returned,
        e.g. "eV/angstrom^2".

    pressure : array containing one float, optional
        The pressure at which the relaxed unstable twinning fault energy is to
        be computed.  This value should be given in the units specified
        by the 'pressure_units' argument.  (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple matching results are found, an error is returned.
        (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to relax the atomic positions in order to compute
        the unstable twinning fault energy for a given lattice constant.
        Currently allowed values are:

      |-----------------------------------+----------------------------------------------------------|
      | Allowed values                    | Description                                              |
      |-----------------------------------|----------------------------------------------------------|
      | "TD_228501831190" \| "relaxation" | Polak-Ribiere conjugate gradient minimization. (default) |
      |-----------------------------------+----------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [unstable_twinning_fault_energy] : array containing one float
        The relaxed unstable twinning fault energy of the monoatomic FCC
        crystal in the requested units.

    """
    return _send_query(locals(), "get_unstable_twinning_fault_relaxed_energy_fcc")


def get_surface_energy_ideal_cubic(
    model, crystal, species, miller, units, method=["TD_955413365818"]
):
    r"""Retrieve ideal surface energy of a high-symmetry surface in a cubic
    crystal comprised of one or more species at zero temperature and pressure,
    as computed by the latest current version of the
    SurfaceEnergyCubicCrystalBrokenBondFit Test Driver (TD_955413365818).

    KIM Property Definition: [surface-energy-ideal-cubic-crystal](https://openkim.org/properties/show/2014-05-21/staff@noreply.openkim.org/surface-energy-ideal-cubic-crystal)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query Eideal get_surface_energy_ideal_cubic crystal=["fcc"] miller=[1,0,0] species=["Al"] units=["eV/angstrom^2"]
      ```

    python:

      ```
      from kim_query import get_surface_energy_ideal_cubic
      get_surface_energy_ideal_cubic(["MO_123629422045_005"], ["fcc"], ["Al"], [1,0,0], ["eV/angstrom^2"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_123629422045_005"]' \
           --data-urlencode 'species=["Al"]'                \
           --data-urlencode 'units=["eV/angstrom^2"]'       \
           https://query.openkim.org/api/get_surface_energy_ideal_cubic
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the cubic crystal.  Currently allowed values are
        "bcc", "diamond", "fcc", and "sc".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the
        crystal, e.g. "Al".

    miller : array of three integers
        The miller indices of the surface.  Currently allowed values are [1,0,0],
        [1,1,0], [1,1,1], [1,2,1].

    units : array containing one double-quoted string
        A physical unit of energy per unit area supported by [GNU units](https://www.gnu.org/software/units/)
        in which the relaxed intrinsic stacking fault energy will be returned,
        e.g. "eV/angstrom^2".

    method : array containing one double-quoted string, optional
        The Test Driver used to compute the ideal surface energy for a given lattice
        constant.  Currently allowed values are:

      |-----------------------------------+----------------------------------------------------------|
      | Allowed values                    | Description                                              |
      |-----------------------------------|----------------------------------------------------------|
      | "TD_955413365818"                 | Corresponds to the lineage SurfaceEnergyCubicCrystalBrokenBondFit__TD_955413365818. (default) |
      |-----------------------------------+----------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [ideal_surface_energy] : array containing one float
        The ideal surface energy in the requested units.

    """
    return _send_query(locals(), "get_surface_energy_ideal_cubic")


def get_surface_energy_relaxed_cubic(
    model,
    crystal,
    species,
    miller,
    units,
    temperature=[0.0],
    temperature_units=["K"],
    temperature_tol=[0.1],
    pressure=[0.0],
    pressure_units=["MPa"],
    pressure_tol=[0.1],
    method=["fire"],
):
    r"""Retrieve free energy of a cubic relaxed surface energy of a
    high-symmetry surface in a cubic crystal comprised of one or more species
    at a given temperature and hydrostatic pressure.  This corresponds to the
    'relaxed' surface energy found by performing an energy minimization.  At
    zero temperature, this corresponds to the potential energy rather than the
    free energy.

    KIM Property Definition: [surface-energy-cubic-crystal-npt](https://openkim.org/properties/show/2014-05-21/staff@noreply.openkim.org/surface-energy-cubic-crystal-npt)

    Usage Examples
    --------------
    LAMMPS:

      ```
      kim_init EAM_Dynamo_ErcolessiAdams_1994_Al__MO_123629422045_005 metal
      kim_query Erelaxed get_surface_energy_relaxed_cubic crystal=["fcc"] miller=[1,0,0] species=["Al"] units=["eV/angstrom^2"]
      ```

    python:

      ```
      from kim_query import get_surface_energy_relaxed_cubic
      get_surface_energy_relaxed_cubic(["MO_123629422045_005"], ["fcc"], ["Al"], [1,0,0], ["eV/angstrom^2"])
      ```

    curl:

      ```
      curl --data-urlencode 'model=["MO_123629422045_005"]' \
           --data-urlencode 'species=["Al"]'                \
           --data-urlencode 'units=["eV/angstrom^2"]'       \
           https://query.openkim.org/api/get_surface_relaxed_ideal_cubic
      ```

    Parameters
    ----------
    model : array containing one double-quoted string
        The KIM ID of the model used to compute the result

    crystal : array containing one double-quoted string
        The short name of the cubic crystal.  Currently allowed values are
        "bcc", "diamond", "fcc", and "sc".

    species : array of double-quoted strings
        The standard chemical symbol(s) of the atomic species comprising the
        crystal, e.g. "Al".

    miller : array of three integers
        The miller indices of the surface.  Currently allowed values are [1,0,0],
        [1,1,0], [1,1,1], [1,2,1].

    units : array containing one double-quoted string
        A physical unit of energy per unit area supported by [GNU units](https://www.gnu.org/software/units/)
        in which the relaxed intrinsic stacking fault energy will be returned,
        e.g. "eV/angstrom^2".

    temperature : array containing one float, optional
        The temperature at which the surface energy is computed.  This value
        should be given in the units specified by the 'temperature_units'
        argument.  (Default: 0.0)

    temperature_units : array containing one double-quoted string, optional
        A physical unit of temperature supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'temperature' argument is given.  (Default: K)

    temperature_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        temperature specified in the given temperature units.  For example, if
        temperature_tol=0.1, temperature=293.15, temperature_units="K", then
        results retrieved by the query must be computed at a temperature of
        293.15 +/- 0.1 K.  If multiple matching results are found, an error is
        returned.  (Default: 0.1)

    pressure : array containing one float, optional
        The pressure at which the surface energy is computed.  This value
        should be given in the units specified by the 'pressure_units'
        argument.  (Default: 0.0)

    pressure_units : array containing one double-quoted string, optional
        A physical unit of pressure supported by [GNU units](https://www.gnu.org/software/units/)
        in which the 'pressure' argument is given.  (Default: MPa)

    pressure_tol : array containing one float, optional
        Indicates a tolerance within which the query results must match the
        pressure specified in the given pressure units.  For example, if
        pressure_tol=0.1, pressure=0.101325, pressure_units="MPa", then results
        retrieved by the query must be computed at a pressure of 0.101325 +/-
        0.1 MPa.  If multiple matching results are found, an error is returned.
        (Default: 0.1)

    method : array containing one double-quoted string, optional
        The algorithm used to minimize the surface energy with respect to the
        atomic positions.  Currently allowed values are:

      |-----------------------------+----------------------------------------------------------|
      | Allowed values              | Description                                              |
      |-----------------------------|----------------------------------------------------------|
      | "TD_955413365818" \| "fire" | Minimization performed using the FIRE damped dynamics method [Bitzek, Koskinen, Gahler, Moseler, Gumbsch, Phys Rev Lett, 97, 170201 (2006)]. (default) |
      |-----------------------------+----------------------------------------------------------|
      {:class="table table-bordered"}
      {:style="width:70%; margin-left:20px;"}
      {:.table-striped}

    Returns
    -------
    [relaxed_surface_energy] : array containing one float
        The relaxed surface energy in the requested units.

    """
    return _send_query(locals(), "get_surface_energy_relaxed_cubic")


# If called directly, do nothing
if __name__ == "__main__":
    pass
