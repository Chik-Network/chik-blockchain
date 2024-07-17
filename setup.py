from __future__ import annotations

import os
import sys

from setuptools import find_packages, setup

dependencies = [
    "aiofiles==23.2.1",  # Async IO for files
    "anyio==4.3.0",
    "boto3==1.34.114",  # AWS S3 for DL s3 plugin
    "chikvdf==1.1.4",  # timelord and vdf verification
    "chikbip158==1.5.1",  # bip158-style wallet filters
    "chikpos==2.0.4",  # proof of space
    "klvm==0.9.10",
    "klvm_tools==0.4.9",  # Currying, Program.to, other conveniences
    "chik_rs==0.9.0",
    "klvm-tools-rs==0.1.40",  # Rust implementation of klvm_tools' compiler
    "aiohttp==3.9.4",  # HTTP server for full node rpc
    "aiosqlite==0.20.0",  # asyncio wrapper for sqlite, to store blocks
    "bitstring==4.1.4",  # Binary data management library
    "colorama==0.4.6",  # Colorizes terminal output
    "colorlog==6.8.2",  # Adds color to logs
    "concurrent-log-handler==0.9.25",  # Concurrently log and rotate logs
    "cryptography==42.0.5",  # Python cryptography library for TLS - keyring conflict
    "filelock==3.14.0",  # For reading and writing config multiprocess and multithread safely  (non-reentrant locks)
    "importlib-resources==6.4.0",
    "keyring==25.1.0",  # Store keys in MacOS Keychain, Windows Credential Locker
    "PyYAML==6.0.1",  # Used for config file format
    "setproctitle==1.3.3",  # Gives the chik processes readable names
    "sortedcontainers==2.4.0",  # For maintaining sorted mempools
    "click==8.1.3",  # For the CLI
    "dnspython==2.6.1",  # Query DNS seeds
    "watchdog==4.0.0",  # Filesystem event watching - watches keyring.yaml
    "dnslib==0.9.24",  # dns lib
    "typing-extensions==4.11.0",  # typing backports like Protocol and TypedDict
    "zstd==1.5.5.1",
    "packaging==24.0",
    "psutil==5.9.4",
    "hsmk==0.3.2",
]

upnp_dependencies = [
    "miniupnpc==2.2.2",  # Allows users to open ports on their router
]

dev_dependencies = [
    "build==1.2.1",
    "coverage==7.5.3",
    "diff-cover==9.0.0",
    "pre-commit==3.5.0; python_version < '3.9'",
    "pre-commit==3.7.1; python_version >= '3.9'",
    "py3createtorrent==1.2.0",
    "pylint==3.2.2",
    "pytest==8.1.1",
    "pytest-cov==5.0.0",
    "pytest-mock==3.14.0",
    "pytest-xdist==3.6.1",
    "pyupgrade==3.15.2",
    "twine==5.1.0",
    "isort==5.13.2",
    "flake8==7.0.0",
    "mypy==1.10.0",
    "black==24.4.2",
    "lxml==5.2.2",
    "aiohttp_cors==0.7.0",  # For blackd
    "pyinstaller==6.7.0",
    "types-aiofiles==23.2.0.20240311",
    "types-cryptography==3.3.23.2",
    "types-pyyaml==6.0.12.20240311",
    "types-setuptools==70.0.0.20240524",
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
