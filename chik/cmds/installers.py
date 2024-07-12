from __future__ import annotations

import json
import subprocess
import tempfile
from typing import Dict, List, Optional

import click
import packaging.version

from chik.daemon.server import executable_for_service
from chik.util.timing import adjusted_timeout


def check_plotter(plotter: List[str], expected_output: bytes, specify_tmp: bool = True) -> None:
    with tempfile.TemporaryDirectory() as path:
        tmp_dir = []
        if specify_tmp:
            tmp_dir = ["--tmp_dir", path]
        process = subprocess.Popen(
            [executable_for_service("chik"), "plotters", *plotter, *tmp_dir, "--final_dir", path],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        out: Optional[bytes]
        err: Optional[bytes]
        try:
            out, err = process.communicate(timeout=2)
        except subprocess.TimeoutExpired as e:
            err = e.stderr
            out = e.stdout
        else:
            print(repr(err))
            print(repr(out))
            assert False, "expected to time out"
        finally:
            process.kill()
            process.communicate()

        assert err is None, repr(err)
        assert out is not None
        assert out.startswith(expected_output), repr(out)


@click.group("installers", help="Installer related helpers such as installer testing")
def installers_group() -> None:
    pass


@installers_group.command(name="test")
@click.option("--expected-chik-version", "expected_chik_version_str", required=True)
@click.option("--require-madmax/--require-no-madmax", "require_madmax", default=True)
def test_command(expected_chik_version_str: str, require_madmax: bool) -> None:
    print("testing installed executables")
    expected_chik_version = packaging.version.Version(expected_chik_version_str)

    args = [executable_for_service("chik"), "version"]
    print(f"launching: {args}")
    chik_version_process = subprocess.run(
        args,
        capture_output=True,
        encoding="utf-8",
        timeout=adjusted_timeout(30),
    )
    assert chik_version_process.returncode == 0
    assert chik_version_process.stderr == ""

    chik_version = packaging.version.Version(chik_version_process.stdout)
    print(chik_version)
    assert chik_version == expected_chik_version, f"{chik_version} != {expected_chik_version}"

    args = [executable_for_service("chik"), "plotters", "version"]
    print(f"launching: {args}")
    plotter_version_process = subprocess.run(
        args,
        capture_output=True,
        encoding="utf-8",
        timeout=adjusted_timeout(30),
    )

    print()
    print(plotter_version_process.stdout)
    print()
    print(plotter_version_process.stderr)
    print()

    assert plotter_version_process.returncode == 0
    assert plotter_version_process.stderr == ""

    found_start = False
    plotter_versions: Dict[str, packaging.version.Version] = {}
    for line in plotter_version_process.stdout.splitlines():
        if line.startswith("chikpos:"):
            found_start = True

        if not found_start:
            continue

        plotter, version = (segment.strip() for segment in line.split(":", maxsplit=1))
        plotter_versions[plotter] = packaging.version.Version(version)

    print(json.dumps({plotter: str(version) for plotter, version in plotter_versions.items()}, indent=4))
    expected = {"chikpos", "bladebit"}

    if require_madmax:
        expected.add("madmax")

    assert plotter_versions.keys() == expected, f"{expected=}"

    # TODO: figure out a better test, these actually start plots which can use up disk
    #       space too fast

    # check_plotter(plotter=["chikpos"], expected_output=b"\nStarting plotting progress")
    # check_plotter(plotter=["madmax"], expected_output=b"Multi-threaded pipelined Chik")
    # check_plotter(plotter=["bladebit", "diskplot", "--compress", "0"], expected_output=b"\nBladebit Chik Plotter")
    # check_plotter(plotter=["bladebit", "cudaplot", "--compress", "0"], expected_output=b"\nBladebit Chik Plotter")
    # check_plotter(
    #     plotter=["bladebit", "ramplot", "--compress", "0"],
    #     expected_output=b"\nBladebit Chik Plotter",
    #     specify_tmp_dir=False,
    # )

    args = [executable_for_service("chik"), "init"]
    print(f"launching: {args}")
    subprocess.run(
        args,
        check=True,
        timeout=adjusted_timeout(30),
    )
