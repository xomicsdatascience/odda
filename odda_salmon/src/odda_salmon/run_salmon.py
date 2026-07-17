# Salmon MCP Server
#
# Provides MCP tools for running Salmon RNA-seq quantification via Apptainer
# containers: building a transcriptome index (salmon index), quantifying reads
# (salmon quant), listing available Salmon versions, and describing Salmon's
# command-line arguments.
#
# The deployment host has a broken `apptainer instance start` (dbus/cgroups),
# so unlike the proteomics servers this module does NOT rely on running
# instances. Instead it resolves a concrete salmon_v{version}.sif image and
# executes it directly with `apptainer run <sif> <subcommand> <args...>` (the
# container runscript is `exec /usr/local/bin/salmon "$@"`). Versions are
# discovered from the built salmon_v*.sif images and, for parity with the other
# servers, from any running Apptainer instances.

from odda_utils.async_exec import execute_process
from odda_salmon import salmon_sif_format
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import asyncio
import contextlib
import os
import re
from mcp.server.fastmcp import FastMCP

app = FastMCP("salmon_multiversion")

# Matches image files named e.g. "salmon_v2.3.3.sif" and captures the version.
_SIF_PATTERN = re.compile(r"^salmon_v(.+)\.sif$")
# Matches running Apptainer instances named e.g. "salmon_v2.3.3".
_INSTANCE_PATTERN = re.compile(r"^salmon_v(.+)$")


def _version_sort_key(version: str):
    """
    Build a sort key for a dotted numeric version string.

    Parameters
    ----------
    version : str
        Version string such as "2.3.3".

    Returns
    -------
    tuple
        Tuple of integer components; unparseable versions sort lowest.
    """
    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError:
        return (-1,)


def _sif_dir() -> Path:
    """
    Resolve the directory that holds the built Salmon Apptainer images.

    By default this is the package-relative ``static/apptainer`` directory
    (``odda_salmon/static/apptainer``). It can be overridden with the
    ``ODDA_SALMON_SIF_DIR`` environment variable, which is useful when the
    images are stored outside the source tree.

    Returns
    -------
    pathlib.Path
        Directory expected to contain ``salmon_v*.sif`` image files.
    """
    override = os.environ.get("ODDA_SALMON_SIF_DIR")
    if override:
        return Path(override)
    # run_salmon.py lives at odda_salmon/src/odda_salmon/run_salmon.py, so the
    # package root (odda_salmon) is three parents up.
    return Path(__file__).resolve().parents[2] / "static" / "apptainer"


def _discover_sif_versions() -> Dict[str, str]:
    """
    Discover available Salmon versions from built ``salmon_v*.sif`` images.

    Returns
    -------
    Dict[str, str]
        Mapping of version string to the absolute path of the matching image.
        Empty if the image directory does not exist or contains no images.
    """
    directory = _sif_dir()
    versions: Dict[str, str] = {}
    if not directory.is_dir():
        return versions
    for image in directory.glob("salmon_v*.sif"):
        match = _SIF_PATTERN.match(image.name)
        if match:
            versions[match.group(1)] = str(image.resolve())
    return versions


def _resolve_sif(version: Optional[str]) -> Dict[str, Any]:
    """
    Resolve a Salmon version to a concrete ``.sif`` image path.

    Parameters
    ----------
    version : Optional[str]
        Explicit bare version string (e.g. "2.3.3"), or None to auto-select the
        newest available image.

    Returns
    -------
    Dict[str, Any]
        ``{"ok": True, "version": <str>, "sif": <path>}`` on success, otherwise
        ``{"ok": False, "error": <str>}``.
    """
    available = _discover_sif_versions()

    if version:
        if version in available:
            return {"ok": True, "version": version, "sif": available[version]}
        # Fall back to the conventional filename in case glob missed it.
        candidate = _sif_dir() / salmon_sif_format.format(version=version)
        if candidate.is_file():
            return {"ok": True, "version": version, "sif": str(candidate.resolve())}
        return {
            "ok": False,
            "error": (
                f"No Salmon image found for version {version!r} in {_sif_dir()}. "
                "Build it with static/apptainer/build_images.sh or pass a version "
                "reported by list_salmon_versions."
            ),
        }

    if not available:
        return {
            "ok": False,
            "error": (
                f"No Salmon .sif images found in {_sif_dir()}. Build one with "
                "static/apptainer/build_images.sh, or set ODDA_SALMON_SIF_DIR to "
                "the directory containing salmon_v*.sif images."
            ),
        }

    newest = max(available, key=_version_sort_key)
    return {"ok": True, "version": newest, "sif": available[newest]}


async def _exec_salmon(
    subcommand: str,
    sub_args: List[str],
    version: Optional[str],
    env: Optional[dict] = None,
    timeout_sec: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Resolve a Salmon image and execute a subcommand inside it directly.

    The container is executed with ``apptainer run <sif> <subcommand> <args>``;
    since the runscript forwards its arguments to the ``salmon`` binary, this is
    equivalent to running ``salmon <subcommand> <args>``. Apptainer auto-mounts
    ``$HOME``, so host paths under the home directory resolve unchanged inside
    the container.

    Parameters
    ----------
    subcommand : str
        Salmon subcommand to run (e.g. "index" or "quant").
    sub_args : list of str
        Arguments to pass to the subcommand.
    version : Optional[str]
        Bare Salmon version (e.g. "2.3.3"), or None to auto-select the newest
        available image.
    env : dict, optional
        Environment variables to set; overrides the current environment.
    timeout_sec : float, optional
        Time in seconds before killing the process.

    Returns
    -------
    Dict[str, Any]
        On an image-resolution failure, ``{"ok": False, "error": <str>}``.
        Otherwise the dictionary returned by ``execute_process`` (keys
        ``exit_code``, ``stdout``, ``stderr``, ``cmd``, ``timed_out``).
    """
    exec_env = os.environ.copy()
    if env:
        exec_env.update({str(k): str(v) for k, v in env.items()})

    resolved = _resolve_sif(version)
    if not resolved["ok"]:
        return resolved

    cmd = ["apptainer", "run", resolved["sif"], subcommand, *sub_args]
    return await execute_process(cmd, env=exec_env, timeout_sec=timeout_sec)


@app.tool()
async def build_salmon_index(
    transcriptome_fasta: str,
    index_dir: str,
    decoys: Optional[str] = None,
    kmer: Optional[int] = None,
    threads: Optional[int] = None,
    keep_duplicates: bool = False,
    gencode: bool = False,
    version: Optional[str] = None,
    env: Optional[dict] = None,
    timeout_sec: Optional[int] = None,
    extra_args: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Build a Salmon transcriptome index by running ``salmon index``.

    The index is required before quantifying reads with :func:`run_salmon`. The
    container is executed directly from its ``.sif`` image; paths must be visible
    inside the container (paths under ``$HOME`` are auto-mounted).

    Parameters
    ----------
    transcriptome_fasta : str
        Path to the transcriptome FASTA file to index (``-t``). For a
        decoy-aware index this should be the concatenated transcriptome+decoy
        FASTA (gentrome).
    index_dir : str
        Output directory in which the Salmon index will be written (``-i``).
    decoys : str, optional
        Path to a text file listing decoy sequence names (``-d``) for a
        decoy-aware index.
    kmer : int, optional
        k-mer length used to build the index (``-k``); Salmon defaults to 31.
    threads : int, optional
        Number of threads to use while building the index (``-p``).
    keep_duplicates : bool, optional
        If True, retain duplicate transcript sequences (``--keepDuplicates``).
    gencode : bool, optional
        If True, treat the FASTA as GENCODE-formatted (``--gencode``).
    version : str, optional
        Bare Salmon version to use (e.g. "2.3.3"). If omitted (None), the newest
        available image is auto-selected.
    env : dict, optional
        Environment variables to set; overrides the current environment.
    timeout_sec : int, optional
        Time in seconds before killing the process.
    extra_args : list of str, optional
        Additional raw arguments appended verbatim to the ``salmon index``
        command (e.g. ["--sparse"]).

    Returns
    -------
    Dict[str, Any]
        On an image-resolution or validation failure,
        ``{"ok": False, "error": <str>}``. Otherwise the dictionary returned by
        ``execute_process`` with keys ``exit_code``, ``stdout``, ``stderr``,
        ``cmd`` and ``timed_out``.
    """
    if not transcriptome_fasta:
        return {"ok": False, "error": "transcriptome_fasta is required."}
    if not index_dir:
        return {"ok": False, "error": "index_dir is required."}

    args: List[str] = ["-t", transcriptome_fasta, "-i", index_dir]
    if decoys:
        args.extend(["-d", decoys])
    if kmer is not None:
        args.extend(["-k", str(kmer)])
    if threads is not None:
        args.extend(["-p", str(threads)])
    if keep_duplicates:
        args.append("--keepDuplicates")
    if gencode:
        args.append("--gencode")
    if extra_args:
        args.extend(extra_args)

    # Salmon creates the index directory itself; ensure its parent exists.
    Path(index_dir).parent.mkdir(parents=True, exist_ok=True)

    return await _exec_salmon("index", args, version, env=env, timeout_sec=timeout_sec)


@app.tool()
async def run_salmon(
    index_dir: str,
    output_dir: str,
    mates1: Optional[List[str]] = None,
    mates2: Optional[List[str]] = None,
    unmated_reads: Optional[List[str]] = None,
    lib_type: str = "A",
    threads: Optional[int] = None,
    gc_bias: bool = False,
    seq_bias: bool = False,
    validate_mappings: bool = False,
    version: Optional[str] = None,
    env: Optional[dict] = None,
    timeout_sec: Optional[int] = None,
    extra_args: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Quantify RNA-seq reads against a Salmon index by running ``salmon quant``.

    Provide either paired-end reads (both ``mates1`` and ``mates2``) or
    single-end reads (``unmated_reads``). The container is executed directly
    from its ``.sif`` image; paths must be visible inside the container (paths
    under ``$HOME`` are auto-mounted).

    Parameters
    ----------
    index_dir : str
        Path to the Salmon index directory produced by
        :func:`build_salmon_index` (``-i``).
    output_dir : str
        Output directory for the quantification results (``-o``). Salmon writes
        ``quant.sf`` and auxiliary files here.
    mates1 : list of str, optional
        Files containing the #1 mates of paired-end reads (``-1``). Must be given
        together with ``mates2``.
    mates2 : list of str, optional
        Files containing the #2 mates of paired-end reads (``-2``). Must be given
        together with ``mates1``.
    unmated_reads : list of str, optional
        Files containing single-end (unmated) reads (``-r``). Mutually exclusive
        with ``mates1``/``mates2``.
    lib_type : str, optional
        Library type string (``-l``); "A" (default) lets Salmon infer it.
    threads : int, optional
        Number of threads to use during quantification (``-p``).
    gc_bias : bool, optional
        If True, enable fragment-level GC bias correction (``--gcBias``).
    seq_bias : bool, optional
        If True, enable sequence-specific bias correction (``--seqBias``).
    validate_mappings : bool, optional
        If True, pass ``--validateMappings`` (selective alignment; the default
        behaviour in recent Salmon versions, accepted here for compatibility).
    version : str, optional
        Bare Salmon version to use (e.g. "2.3.3"). If omitted (None), the newest
        available image is auto-selected.
    env : dict, optional
        Environment variables to set; overrides the current environment.
    timeout_sec : int, optional
        Time in seconds before killing the process.
    extra_args : list of str, optional
        Additional raw arguments appended verbatim to the ``salmon quant``
        command (e.g. ["--numBootstraps", "100"]).

    Returns
    -------
    Dict[str, Any]
        On an image-resolution or validation failure,
        ``{"ok": False, "error": <str>}``. Otherwise the dictionary returned by
        ``execute_process`` with keys ``exit_code``, ``stdout``, ``stderr``,
        ``cmd`` and ``timed_out``.

    Examples
    --------
    Quantify a paired-end sample with GC-bias correction::

        run_salmon(
            index_dir="$HOME/data/supporting/salmon_index",
            output_dir="$HOME/data/quantified/GSE12345/v0/sample1",
            mates1=["$HOME/data/datasets/GSE12345/s1_1.fastq.gz"],
            mates2=["$HOME/data/datasets/GSE12345/s1_2.fastq.gz"],
            threads=8,
            gc_bias=True,
        )
    """
    if not index_dir:
        return {"ok": False, "error": "index_dir is required."}
    if not output_dir:
        return {"ok": False, "error": "output_dir is required."}

    paired = bool(mates1) and bool(mates2)
    single = bool(unmated_reads)
    if not paired and not single:
        return {
            "ok": False,
            "error": (
                "Provide paired-end reads (both mates1 and mates2) or single-end "
                "reads (unmated_reads)."
            ),
        }
    if (bool(mates1) != bool(mates2)):
        return {
            "ok": False,
            "error": "Paired-end quantification requires both mates1 and mates2.",
        }
    if paired and single:
        return {
            "ok": False,
            "error": (
                "Specify either paired-end reads (mates1/mates2) or single-end "
                "reads (unmated_reads), not both."
            ),
        }

    args: List[str] = ["-i", index_dir, "-l", lib_type]
    if paired:
        args.append("-1")
        args.extend(mates1)
        args.append("-2")
        args.extend(mates2)
    else:
        args.append("-r")
        args.extend(unmated_reads)
    args.extend(["-o", output_dir])
    if threads is not None:
        args.extend(["-p", str(threads)])
    if gc_bias:
        args.append("--gcBias")
    if seq_bias:
        args.append("--seqBias")
    if validate_mappings:
        args.append("--validateMappings")
    if extra_args:
        args.extend(extra_args)

    # Salmon creates the output directory itself; ensure its parent exists.
    Path(output_dir).parent.mkdir(parents=True, exist_ok=True)

    return await _exec_salmon("quant", args, version, env=env, timeout_sec=timeout_sec)


@app.tool()
async def list_salmon_versions(
    timeout_sec: Optional[float] = 10.0,
) -> Dict[str, Any]:
    """
    List available Salmon versions.

    Salmon versions are discovered primarily from the built ``salmon_v*.sif``
    images in the package image directory. For parity with the other
    quantification servers, running Apptainer/Singularity instances named
    ``salmon_v*`` are also inspected; note that ``apptainer instance start`` is
    broken on the deployment host, so the image-based discovery is authoritative
    and the run/index tools operate on ``.sif`` images regardless of instances.

    Parameters
    ----------
    timeout_sec : float, optional
        Timeout in seconds for the instance list command. Default is 10.0.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
        - ok (bool): Whether any versions were discovered.
        - versions (List[str]): Sorted union of image and instance versions.
        - sif_versions (List[str]): Versions available as built ``.sif`` images.
        - sif_paths (Dict[str, str]): Mapping of version to image path.
        - instance_names (List[str]): Running instance names matching salmon_v*.
        - container_runtime (str, optional): Runtime used to list instances.
        - error (str, optional): Present when no versions were discovered.
    """
    sif_map = _discover_sif_versions()
    sif_versions = sorted(sif_map, key=_version_sort_key)

    instance_versions: List[str] = []
    instance_names: List[str] = []
    container_runtime: Optional[str] = None

    for container_cmd in ["apptainer", "singularity"]:
        cmd = [container_cmd, "instance", "list"]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout_b, _stderr_b = (
                    await asyncio.wait_for(proc.communicate(), timeout=timeout_sec)
                    if timeout_sec
                    else await proc.communicate()
                )
            except asyncio.TimeoutError:
                with contextlib.suppress(ProcessLookupError):
                    proc.kill()
                continue

            if proc.returncode != 0:
                continue

            container_runtime = container_cmd
            stdout_str = stdout_b.decode(errors="replace")
            for line in stdout_str.strip().split("\n"):
                if not line.strip() or line.startswith("INSTANCE NAME"):
                    continue
                parts = line.split()
                if not parts:
                    continue
                match = _INSTANCE_PATTERN.match(parts[0])
                if match:
                    instance_versions.append(match.group(1))
                    instance_names.append(parts[0])
            break
        except FileNotFoundError:
            continue

    all_versions = sorted(
        set(sif_versions) | set(instance_versions), key=_version_sort_key
    )

    result: Dict[str, Any] = {
        "ok": bool(all_versions),
        "versions": all_versions,
        "sif_versions": sif_versions,
        "sif_paths": sif_map,
        "instance_names": instance_names,
    }
    if container_runtime:
        result["container_runtime"] = container_runtime
    if not all_versions:
        result["error"] = (
            f"No Salmon versions found. Looked for salmon_v*.sif images in "
            f"{_sif_dir()} and for running Apptainer instances named salmon_v*."
        )
    return result


@app.tool()
async def get_salmon_argument_info(arg: Optional[Union[str, List[str]]] = None):
    """
    Get documentation for Salmon command-line arguments.

    If called without arguments, returns the full list of documented parameters
    for the ``index`` and ``quant`` subcommands. If called with a single
    argument, returns a description of that argument. If called with a list of
    arguments, returns a description for each.

    Parameters
    ----------
    arg : str or list of str, optional
        The argument or list of arguments for which information is requested.
        Arguments may be given with or without leading dashes (e.g. "-p",
        "--threads", or "threads").

    Returns
    -------
    str
        Description string of the requested argument(s).
    """
    if arg is None or len(arg) == 0:
        from odda_salmon import salmon_all_arguments

        return salmon_all_arguments
    else:
        from odda_salmon import salmon_argument_dict

        if isinstance(arg, str):
            arg = [arg]
        result = ""
        not_found = []
        for a in arg:
            if a not in salmon_argument_dict:
                not_found.append(a)
                continue
            result += f"{a}: {salmon_argument_dict[a]}\n"
        if not_found:
            result += f"\nThe following arguments were not found: {', '.join(not_found)}"
        return result


def main():
    app.run()


if __name__ == "__main__":
    main()
