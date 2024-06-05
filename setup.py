from __future__ import annotations

import os
import sys

from setuptools import find_packages, setup

dependencies = [
    "aiofiles==23.2.1",  # Async IO for files
    "anyio==4.3.0",
    "boto3==1.34.46",  # AWS S3 for DL s3 plugin
    "chikvdf==1.1.4",  # timelord and vdf verification
    "chikbip158==1.4",  # bip158-style wallet filters
    "chikpos==2.0.4",  # proof of space
    "klvm==0.9.9",
    "klvm_tools==0.4.9",  # Currying, Program.to, other conveniences
    "chik_rs==0.6.1",
    "klvm-tools-rs==0.1.40",  # Rust implementation of klvm_tools' compiler
    "aiohttp==3.9.2",  # HTTP server for full node rpc
    "aiosqlite==0.20.0",  # asyncio wrapper for sqlite, to store blocks
    "bitstring==4.1.4",  # Binary data management library
    "colorama==0.4.6",  # Colorizes terminal output
    "colorlog==6.8.2",  # Adds color to logs
    "concurrent-log-handler==0.9.25",  # Concurrently log and rotate logs
    "cryptography==42.0.5",  # Python cryptography library for TLS - keyring conflict
    "filelock==3.13.1",  # For reading and writing config multiprocess and multithread safely  (non-reentrant locks)
    "keyring==24.3.1",  # Store keys in MacOS Keychain, Windows Credential Locker
    "PyYAML==6.0.1",  # Used for config file format
    "setproctitle==1.3.3",  # Gives the chik processes readable names
    "sortedcontainers==2.4.0",  # For maintaining sorted mempools
    "click==8.1.3",  # For the CLI
    "dnspython==2.5.0",  # Query DNS seeds
    "watchdog==4.0.0",  # Filesystem event watching - watches keyring.yaml
    "dnslib==0.9.24",  # dns lib
    "typing-extensions==4.10.0",  # typing backports like Protocol and TypedDict
    "zstd==1.5.5.1",
    "packaging==23.2",
    "psutil==5.9.4",
]

upnp_dependencies = [
    "miniupnpc==2.2.2",  # Allows users to open ports on their router
]

dev_dependencies = [
    "build==1.0.3",
    "coverage==7.4.3",
    "diff-cover==8.0.3",
    "pre-commit==3.5.0; python_version < '3.9'",
    "pre-commit==3.6.2; python_version >= '3.9'",
    "py3createtorrent==1.2.0",
    "pylint==3.0.3",
    "pytest==8.0.2",
    "pytest-cov==4.1.0",
    "pytest-mock==3.12.0",
    "pytest-xdist==3.5.0",
    "pyupgrade==3.15.0",
    "twine==5.0.0",
    "isort==5.13.2",
    "flake8==7.0.0",
    "mypy==1.8.0",
    "black==24.2.0",
    "lxml==5.1.0",
    "aiohttp_cors==0.7.0",  # For blackd
    "pyinstaller==6.5.0",
    "setuptools<70",  # TODO: remove - https://github.com/pypa/setuptools/issues/4374
    "types-aiofiles==23.2.0.20240311",
    "types-cryptography==3.3.23.2",
    "types-pyyaml==6.0.12.12",
    "types-setuptools==69.1.0.20240310",
]

legacy_keyring_dependencies = [
    "keyrings.cryptfile==1.3.9",
]

kwargs = dict(
    name="chik-blockchain",
    author="Mariano Sorgente",
    author_email="admin@chiknetwork.com",
    description="Chik blockchain full node, farmer, timelord, and wallet.",
    url="https://chiknetwork.com/",
    license="Apache License",
    python_requires=">=3.8.1, <4",
    keywords="chik blockchain node",
    install_requires=dependencies,
    extras_require={
        "dev": dev_dependencies,
        "upnp": upnp_dependencies,
        "legacy-keyring": legacy_keyring_dependencies,
    },
    packages=find_packages(include=["build_scripts", "chik", "chik.*", "mozilla-ca"]),
    entry_points={
        "console_scripts": [
            "chik = chik.cmds.chik:main",
            "chik_daemon = chik.daemon.server:main",
            "chik_wallet = chik.server.start_wallet:main",
            "chik_full_node = chik.server.start_full_node:main",
            "chik_harvester = chik.server.start_harvester:main",
            "chik_farmer = chik.server.start_farmer:main",
            "chik_introducer = chik.server.start_introducer:main",
            "chik_crawler = chik.seeder.start_crawler:main",
            "chik_seeder = chik.seeder.dns_server:main",
            "chik_timelord = chik.server.start_timelord:main",
            "chik_timelord_launcher = chik.timelord.timelord_launcher:main",
            "chik_full_node_simulator = chik.simulator.start_simulator:main",
            "chik_data_layer = chik.server.start_data_layer:main",
            "chik_data_layer_http = chik.data_layer.data_layer_server:main",
            "chik_data_layer_s3_plugin = chik.data_layer.s3_plugin_service:run_server",
        ]
    },
    package_data={
        "": ["*.clsp", "*.clsp.hex", "*.klvm", "*.clib", "py.typed"],
        "chik._tests.cmds.wallet": ["test_offer.toffer"],
        "chik._tests.farmer_harvester": ["*.json"],
        "chik._tests.tools": ["*.json", "test-blockchain-db.sqlite"],
        "chik._tests.util": ["bip39_test_vectors.json", "klvm_generator.bin", "protocol_messages_bytes-v*"],
        "chik.util": ["initial-*.yaml", "english.txt"],
        "chik.ssl": ["chik_ca.crt", "chik_ca.key", "dst_root_ca.pem"],
        "mozilla-ca": ["cacert.pem"],
    },
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    zip_safe=False,
    project_urls={
        "Source": "https://github.com/Chik-Network/chik-blockchain/",
        "Changelog": "https://github.com/Chik-Network/chik-blockchain/blob/main/CHANGELOG.md",
    },
)

if "setup_file" in sys.modules:
    # include dev deps in regular deps when run in snyk
    dependencies.extend(dev_dependencies)

if len(os.environ.get("CHIK_SKIP_SETUP", "")) < 1:
    setup(**kwargs)  # type: ignore
