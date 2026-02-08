"""
Vendor dependency validation utilities for supersql.

This module provides utilities to check if required dependencies are installed
for specific database vendors and provides helpful error messages when they're missing.
"""

import importlib
from typing import Dict, List, Optional, Tuple


# Mapping of vendor names to their required dependencies
VENDOR_DEPENDENCIES: Dict[str, List[str]] = {
    "postgres": ["asyncpg"],
    "postgresql": ["asyncpg"],
    "mysql": ["aiomysql"],
    "mariadb": ["aiomysql"],
    "sqlite": ["aiosqlite"],
    "mssql": ["aioodbc", "pyodbc"],
    "sqlserver": ["aioodbc", "pyodbc"],
    "oracle": ["cx_Oracle"],
    "oracledb": ["oracledb"],
    "athena": ["PyAthena"],
    "presto": ["presto-python-client"],
}

# Mapping of vendor names to their pip install extras
VENDOR_EXTRAS: Dict[str, str] = {
    "postgres": "postgres",
    "postgresql": "postgresql",
    "mysql": "mysql",
    "mariadb": "mariadb",
    "sqlite": "sqlite",
    "mssql": "mssql",
    "sqlserver": "sqlserver",
    "oracle": "oracle",
    "oracledb": "oracledb",
    "athena": "athena",
    "presto": "presto",
}


class VendorDependencyError(ImportError):
    """Raised when a required vendor dependency is not installed."""
    
    def __init__(self, vendor: str, missing_deps: List[str], message: Optional[str] = None):
        self.vendor = vendor
        self.missing_deps = missing_deps
        
        if message is None:
            extra = VENDOR_EXTRAS.get(vendor, vendor)
            deps_str = ", ".join(missing_deps)
            message = (
                f"Missing required dependencies for {vendor}: {deps_str}\n"
                f"Install with: pip install supersql[{extra}]\n"
                f"Or manually: pip install {' '.join(missing_deps)}"
            )
        
        super().__init__(message)


def check_vendor_dependencies(vendor: str) -> Tuple[bool, List[str]]:
    """
    Check if all required dependencies for a vendor are installed.
    
    Args:
        vendor: The database vendor name (e.g., 'postgres', 'mysql')
        
    Returns:
        Tuple of (all_installed: bool, missing_dependencies: List[str])
    """
    vendor = vendor.lower()
    required_deps = VENDOR_DEPENDENCIES.get(vendor, [])
    
    if not required_deps:
        # No dependencies required or unknown vendor
        return True, []
    
    missing_deps = []
    
    for dep in required_deps:
        try:
            importlib.import_module(dep)
        except ImportError:
            missing_deps.append(dep)
    
    return len(missing_deps) == 0, missing_deps


def validate_vendor_dependencies(vendor: str) -> None:
    """
    Validate that all required dependencies for a vendor are installed.
    
    Args:
        vendor: The database vendor name
        
    Raises:
        VendorDependencyError: If any required dependencies are missing
    """
    all_installed, missing_deps = check_vendor_dependencies(vendor)
    
    if not all_installed:
        raise VendorDependencyError(vendor, missing_deps)


def get_vendor_dependencies(vendor: str) -> List[str]:
    """
    Get the list of required dependencies for a vendor.
    
    Args:
        vendor: The database vendor name
        
    Returns:
        List of required dependency names
    """
    return VENDOR_DEPENDENCIES.get(vendor.lower(), [])


def is_vendor_supported(vendor: str) -> bool:
    """
    Check if a vendor is supported by supersql.
    
    Args:
        vendor: The database vendor name
        
    Returns:
        True if the vendor is supported, False otherwise
    """
    return vendor.lower() in VENDOR_DEPENDENCIES


def get_installation_command(vendor: str) -> str:
    """
    Get the pip installation command for a vendor's dependencies.
    
    Args:
        vendor: The database vendor name
        
    Returns:
        The pip install command string
    """
    extra = VENDOR_EXTRAS.get(vendor.lower(), vendor.lower())
    return f"pip install supersql[{extra}]"
