# edt-connectivity

A cross-platform Python script that checks access to common programming
resources from the current network. Useful for Yocto developers working
in corporate environments where firewall rules vary.

## What it checks

26 resources across 8 categories, run in parallel:

| Category | Resources |
|---|---|
| **Yocto/OE** | yoctoproject.org, git.yoctoproject.org, openembedded.org, layers.openembedded.org |
| **Kernel** | kernel.org, git.kernel.org, mirrors.kernel.org, freedesktop.org |
| **SCM** | GitHub, GitHub Raw CDN, GitLab, Bitbucket, SourceForge |
| **Packages** | PyPI, npm, Maven Central, crates.io |
| **Containers** | Docker Hub, Docker Registry API, Quay.io |
| **Build** | GNU Project, CMake |
| **OS/Distro** | Debian, Ubuntu |
| **Dev Docs** | Stack Overflow, Read the Docs |

## Sample output

```
========================================================================
 EDT Connectivity Checker — Common Programming Resources
========================================================================
  Timeout : 10s per resource
  Workers : 10 parallel checks
  Total   : 26 resources

  Checking resources..........................

  [ Yocto/OE ]
  Resource                     Status                      Latency  Details
  ---------------------------  --------------------  ------------  ----------------------------
  OE Layer Index               PASS [HTTP 200]           1098 ms  https://layers.openembedded.org
  OpenEmbedded                 PASS [HTTP 200]           1139 ms  https://www.openembedded.org
  Yocto Git                    PASS [HTTP 200]            419 ms  https://git.yoctoproject.org
  Yocto Project                PASS [HTTP 200]           1224 ms  https://www.yoctoproject.org
  ...

========================================================================
 SUMMARY
========================================================================
  Reachable :  26
  Blocked   :   0
  Total     :  26  (100% reachable)

  All resources reachable.
```

Results are color-coded: green for pass, red for fail, yellow for high
latency. The script exits with code `0` if all resources are reachable,
or `1` if any are blocked.

## Requirements

- Python 3.10+
- Internet access (that's the point)

## Setup

### Linux / macOS

```bash
bash setup.sh
source .venv/bin/activate
python check_connectivity.py
```

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
.\.venv\Scripts\Activate.ps1
python check_connectivity.py
```

The setup scripts create a `.venv` virtual environment and install
dependencies from `requirements.txt` (`requests`, `colorama`).

## Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP connectivity checks |
| `colorama` | Cross-platform terminal color output |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All resources reachable |
| `1` | One or more resources unreachable |

## Notes

- Some registry API roots return HTTP 4xx by design (e.g. Docker Registry,
  crates.io). These are still counted as **reachable** — the server answered.
  Only HTTP 5xx responses and connection/timeout errors are counted as failures.
- The timeout per resource is 10 seconds. All checks run concurrently with
  up to 10 worker threads.
