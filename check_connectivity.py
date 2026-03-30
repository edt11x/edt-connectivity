#!/usr/bin/env python3
"""
Connectivity checker for common programming resources.
Useful for Yocto developers working in corporate environments
with variable firewall rules.
"""

import sys
import time
import socket
import concurrent.futures
from dataclasses import dataclass, field
from typing import Optional

import requests
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init(autoreset=True)

TIMEOUT_SECONDS = 10
MAX_WORKERS = 10

@dataclass
class Resource:
    name: str
    url: str
    category: str
    description: str

@dataclass
class Result:
    resource: Resource
    success: bool
    status_code: Optional[int] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None


RESOURCES: list[Resource] = [
    # Yocto / OpenEmbedded
    Resource("Yocto Project",        "https://www.yoctoproject.org",         "Yocto/OE",  "Main Yocto Project site"),
    Resource("Yocto Git",            "https://git.yoctoproject.org",         "Yocto/OE",  "Yocto Git repositories"),
    Resource("OpenEmbedded",         "https://www.openembedded.org",         "Yocto/OE",  "OpenEmbedded project"),
    Resource("OE Layer Index",       "https://layers.openembedded.org",      "Yocto/OE",  "OpenEmbedded layer index"),

    # Kernel & system
    Resource("kernel.org",           "https://www.kernel.org",               "Kernel",    "Linux kernel source"),
    Resource("kernel.org Git",       "https://git.kernel.org",               "Kernel",    "Kernel Git repositories"),
    Resource("kernel.org Mirrors",   "https://mirrors.kernel.org",           "Kernel",    "Kernel.org mirror network"),
    Resource("Freedesktop.org",      "https://www.freedesktop.org",          "Kernel",    "Freedesktop (Mesa, D-Bus, etc.)"),

    # Source control hosting
    Resource("GitHub",               "https://github.com",                   "SCM",       "GitHub code hosting"),
    Resource("GitHub Raw",           "https://raw.githubusercontent.com",    "SCM",       "GitHub raw file delivery CDN"),
    Resource("GitLab",               "https://gitlab.com",                   "SCM",       "GitLab code hosting"),
    Resource("Bitbucket",            "https://bitbucket.org",                "SCM",       "Bitbucket code hosting"),
    Resource("SourceForge",          "https://sourceforge.net",              "SCM",       "SourceForge code hosting"),

    # Package registries
    Resource("PyPI",                 "https://pypi.org",                     "Packages",  "Python Package Index"),
    Resource("npm Registry",         "https://registry.npmjs.org",           "Packages",  "Node.js package registry"),
    Resource("Maven Central",        "https://search.maven.org",             "Packages",  "Java/JVM package registry"),
    Resource("crates.io",            "https://crates.io",                    "Packages",  "Rust package registry"),

    # Container registries
    Resource("Docker Hub",           "https://hub.docker.com",               "Containers","Docker Hub image registry"),
    Resource("Docker Registry API",  "https://registry-1.docker.io",        "Containers","Docker registry API endpoint"),
    Resource("Quay.io",              "https://quay.io",                      "Containers","Red Hat container registry"),

    # Build tools & GNU
    Resource("GNU Project",          "https://www.gnu.org",                  "Build",     "GNU tools and libraries"),
    Resource("CMake",                "https://cmake.org",                    "Build",     "CMake build system"),

    # OS / distro
    Resource("Debian",               "https://www.debian.org",               "OS/Distro", "Debian Linux"),
    Resource("Ubuntu",               "https://ubuntu.com",                   "OS/Distro", "Ubuntu Linux"),

    # Developer resources
    Resource("Stack Overflow",       "https://stackoverflow.com",            "Dev Docs",  "Developer Q&A"),
    Resource("Read the Docs",        "https://readthedocs.org",              "Dev Docs",  "Documentation hosting"),
]


def check_resource(resource: Resource) -> Result:
    """Attempt an HTTP GET to the resource URL and return a Result."""
    start = time.monotonic()
    try:
        response = requests.get(
            resource.url,
            timeout=TIMEOUT_SECONDS,
            allow_redirects=True,
            headers={"User-Agent": "edt-connectivity-checker/1.0"},
        )
        latency_ms = (time.monotonic() - start) * 1000
        # Treat any response (even 4xx/5xx) as reachable — the server answered
        success = response.status_code < 500
        return Result(
            resource=resource,
            success=success,
            status_code=response.status_code,
            latency_ms=latency_ms,
        )
    except requests.exceptions.SSLError as exc:
        latency_ms = (time.monotonic() - start) * 1000
        return Result(resource=resource, success=False,
                      latency_ms=latency_ms, error=f"SSL error: {exc}")
    except requests.exceptions.ConnectionError as exc:
        latency_ms = (time.monotonic() - start) * 1000
        return Result(resource=resource, success=False,
                      latency_ms=latency_ms, error="Connection refused / DNS failure")
    except requests.exceptions.Timeout:
        latency_ms = (time.monotonic() - start) * 1000
        return Result(resource=resource, success=False,
                      latency_ms=latency_ms, error=f"Timeout after {TIMEOUT_SECONDS}s")
    except Exception as exc:  # noqa: BLE001
        latency_ms = (time.monotonic() - start) * 1000
        return Result(resource=resource, success=False,
                      latency_ms=latency_ms, error=str(exc))


def status_str(result: Result) -> str:
    if result.success:
        code = f"HTTP {result.status_code}" if result.status_code else "OK"
        return f"{Fore.GREEN}PASS{Style.RESET_ALL} [{code}]"
    return f"{Fore.RED}FAIL{Style.RESET_ALL}"


def latency_str(result: Result) -> str:
    if result.latency_ms is None:
        return "    —   "
    ms = result.latency_ms
    color = Fore.GREEN if ms < 500 else Fore.YELLOW if ms < 2000 else Fore.RED
    return f"{color}{ms:7.0f} ms{Style.RESET_ALL}"


def print_header() -> None:
    print()
    print(Style.BRIGHT + "=" * 72)
    print(" EDT Connectivity Checker — Common Programming Resources")
    print("=" * 72 + Style.RESET_ALL)
    print(f"  Timeout : {TIMEOUT_SECONDS}s per resource")
    print(f"  Workers : {MAX_WORKERS} parallel checks")
    print(f"  Total   : {len(RESOURCES)} resources")
    print()


def print_results(results: list[Result]) -> None:
    current_category = None
    for result in results:
        cat = result.resource.category
        if cat != current_category:
            current_category = cat
            print(f"\n  {Style.BRIGHT}{Fore.CYAN}[ {cat} ]{Style.RESET_ALL}")
            print(f"  {'Resource':<28} {'Status':<22} {'Latency':>12}  {'Details'}")
            print(f"  {'-'*27}  {'-'*20}  {'-'*12}  {'-'*28}")

        status = status_str(result)
        lat    = latency_str(result)
        detail = result.error or result.resource.url
        if len(detail) > 42:
            detail = detail[:39] + "..."

        print(f"  {result.resource.name:<28} {status:<31} {lat}  {detail}")


def print_summary(results: list[Result]) -> None:
    passed  = [r for r in results if r.success]
    failed  = [r for r in results if not r.success]
    pct     = len(passed) / len(results) * 100

    print()
    print(Style.BRIGHT + "=" * 72)
    print(" SUMMARY")
    print("=" * 72 + Style.RESET_ALL)
    print(f"  {Fore.GREEN}Reachable : {len(passed):>3}{Style.RESET_ALL}")
    print(f"  {Fore.RED}Blocked   : {len(failed):>3}{Style.RESET_ALL}")
    print(f"  Total     : {len(results):>3}  ({pct:.0f}% reachable)")

    if failed:
        print()
        print(f"  {Style.BRIGHT}{Fore.RED}Unreachable resources:{Style.RESET_ALL}")
        for r in failed:
            err = f" — {r.error}" if r.error else ""
            print(f"    {Fore.RED}✗{Style.RESET_ALL}  {r.resource.name:<28}  {r.resource.url}{err}")

    print()
    if len(passed) == len(results):
        print(f"  {Fore.GREEN}{Style.BRIGHT}All resources reachable.{Style.RESET_ALL}")
    elif len(passed) == 0:
        print(f"  {Fore.RED}{Style.BRIGHT}No resources reachable — check your network connection.{Style.RESET_ALL}")
    else:
        print(f"  {Fore.YELLOW}{Style.BRIGHT}Partial connectivity — some resources may be firewall-blocked.{Style.RESET_ALL}")
    print()


def main() -> int:
    print_header()
    print("  Checking resources", end="", flush=True)

    # Sort resources so output groups by category
    resources = sorted(RESOURCES, key=lambda r: (r.category, r.name))

    results: list[Result] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(check_resource, r): r for r in resources}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            print(".", end="", flush=True)

    # Re-sort results to match category order for display
    results.sort(key=lambda r: (r.resource.category, r.resource.name))

    print()
    print_results(results)
    print_summary(results)

    failed_count = sum(1 for r in results if not r.success)
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
