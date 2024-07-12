from __future__ import annotations

import importlib
import inspect
import os
import pathlib
import sys
import tempfile
from typing import List

import importlib_resources
from klvm_tools_rs import compile_klvm as compile_klvm_rust

from chik.types.blockchain_format.program import Program
from chik.types.blockchain_format.serialized_program import SerializedProgram
from chik.util.lock import Lockfile

compile_klvm_py = None

recompile_requested = (
    (os.environ.get("CHIK_DEV_COMPILE_KLVM_ON_IMPORT", "") != "") or ("pytest" in sys.modules)
) and os.environ.get("CHIK_DEV_COMPILE_KLVM_DISABLED", None) is None

here_name = __name__.rpartition(".")[0]


def translate_path(p_):
    p = str(p_)
    if os.path.isdir(p):
        return p
    else:
        module_object = importlib.import_module(p)
        return os.path.dirname(inspect.getfile(module_object))


# Handle optional use of python klvm_tools if available and requested
if "KLVM_TOOLS" in os.environ:
    from klvm_tools.klvmc import compile_klvm as compile_klvm_py_candidate

    compile_klvm_py = compile_klvm_py_candidate


def compile_klvm_in_lock(full_path: pathlib.Path, output: pathlib.Path, search_paths: List[pathlib.Path]):
    # Compile using rust (default)

    # Ensure path translation is done in the idiomatic way currently
    # expected.  It can use either a filesystem path or name a python
    # module.
    treated_include_paths = list(map(translate_path, search_paths))
    res = compile_klvm_rust(str(full_path), str(output), treated_include_paths)

    if "KLVM_TOOLS" in os.environ and os.environ["KLVM_TOOLS"] == "check" and compile_klvm_py is not None:
        # Simple helper to read the compiled output
        def sha256file(f):
            import hashlib

            m = hashlib.sha256()
            m.update(open(f).read().strip().encode("utf8"))
            return m.hexdigest()

        orig = "%s.orig" % output

        compile_klvm_py(full_path, orig, search_paths=search_paths)
        orig256 = sha256file(orig)
        rs256 = sha256file(output)

        if orig256 != rs256:
            print(f"Compiled original {full_path}: {orig256} vs rust {rs256}\n")
            print("Aborting compilation due to mismatch with rust")
            assert orig256 == rs256
        else:
            print(f"Compilation match {full_path}: {orig256}\n")

    return res


def compile_klvm(full_path: pathlib.Path, output: pathlib.Path, search_paths: List[pathlib.Path] = []):
    with Lockfile.create(pathlib.Path(tempfile.gettempdir()) / "klvm_compile" / full_path.name):
        compile_klvm_in_lock(full_path, output, search_paths)


def load_serialized_klvm(
    klvm_filename, package_or_requirement=here_name, include_standard_libraries: bool = True, recompile: bool = True
) -> SerializedProgram:
    """
    This function takes a .clsp file in the given package and compiles it to a
    .clsp.hex file if the .hex file is missing or older than the .clsp file, then
    returns the contents of the .hex file as a `Program`.

    klvm_filename: file name
    package_or_requirement: usually `__name__` if the klvm file is in the same package
    """
    hex_filename = f"{klvm_filename}.hex"

    # Set the CHIK_DEV_COMPILE_KLVM_ON_IMPORT environment variable to anything except
    # "" or "0" to trigger automatic recompilation of the Chiklisp on load.
    resources = importlib_resources.files(package_or_requirement)
    if recompile and not getattr(sys, "frozen", False):
        full_path = resources.joinpath(klvm_filename)
        if full_path.exists():
            # Establish whether the size is zero on entry
            output = full_path.parent / hex_filename
            if not output.exists() or os.stat(full_path).st_mtime > os.stat(output).st_mtime:
                search_paths = [full_path.parent]
                if include_standard_libraries:
                    # we can't get the dir, but we can get a file then get its parent.
                    chik_puzzles_path = pathlib.Path(__file__).parent
                    search_paths.append(chik_puzzles_path)
                compile_klvm(full_path, output, search_paths=search_paths)

    klvm_path = resources.joinpath(hex_filename)
    klvm_hex = klvm_path.read_text(encoding="utf-8")
    assert len(klvm_hex.strip()) != 0
    klvm_blob = bytes.fromhex(klvm_hex)
    return SerializedProgram.from_bytes(klvm_blob)


def load_klvm(
    klvm_filename,
    package_or_requirement=here_name,
    include_standard_libraries: bool = True,
    recompile: bool = True,
) -> Program:
    return Program.from_bytes(
        bytes(
            load_serialized_klvm(
                klvm_filename,
                package_or_requirement=package_or_requirement,
                include_standard_libraries=include_standard_libraries,
                recompile=recompile,
            )
        )
    )


def load_klvm_maybe_recompile(
    klvm_filename,
    package_or_requirement=here_name,
    include_standard_libraries: bool = True,
    recompile: bool = recompile_requested,
) -> Program:
    return load_klvm(
        klvm_filename=klvm_filename,
        package_or_requirement=package_or_requirement,
        include_standard_libraries=include_standard_libraries,
        recompile=recompile,
    )


def load_serialized_klvm_maybe_recompile(
    klvm_filename,
    package_or_requirement=here_name,
    include_standard_libraries: bool = True,
    recompile: bool = recompile_requested,
) -> SerializedProgram:
    return load_serialized_klvm(
        klvm_filename=klvm_filename,
        package_or_requirement=package_or_requirement,
        include_standard_libraries=include_standard_libraries,
        recompile=recompile,
    )
