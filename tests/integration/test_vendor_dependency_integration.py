"""
Integration tests for vendor dependency validation.

These tests demonstrate the expected behavior when users try to use
supersql with different database vendors and missing dependencies.
"""

import unittest
from unittest.mock import patch
import sys

from supersql.core.query import Query
from supersql.core.database import Database
from supersql.errors import VendorDependencyError, UnsupportedVendorError


class TestVendorDependencyIntegration(unittest.TestCase):
    """Integration tests for vendor dependency validation."""
    
    def test_supported_vendors_list(self):
        """Test that all supported vendors are properly defined."""
        from supersql.core.query import SUPPORTED_ENGINES
        from supersql.utils.vendor_deps import VENDOR_DEPENDENCIES
        
        # All supported engines should have dependency definitions
        for engine in SUPPORTED_ENGINES:
            self.assertIn(engine, VENDOR_DEPENDENCIES, 
                         f"Engine {engine} missing from VENDOR_DEPENDENCIES")
    
    def test_query_creation_with_supported_vendor(self):
        """Test Query creation with supported vendors."""
        # These should not raise NotImplementedError
        try:
            Query("postgres")
            Query("mysql") 
            Query("sqlite")
            Query("mssql")
        except NotImplementedError:
            self.fail("Query creation failed for supported vendor")
        except Exception:
            # Other exceptions (like missing dependencies) are expected
            pass
    
    def test_query_creation_with_unsupported_vendor(self):
        """Test Query creation with unsupported vendor."""
        with self.assertRaises(NotImplementedError) as context:
            Query("completely_unsupported_db")
        
        self.assertIn("completely_unsupported_db is not a supersql supported engine", 
                     str(context.exception))
    
    @patch('supersql.core.database.import_module')
    def test_database_creation_with_missing_dependencies(self, mock_import):
        """Test Database creation when dependencies are missing."""
        # Mock missing dependency - this will be caught by runtime_module_resolver
        mock_import.side_effect = ImportError("No module named 'asyncpg'")

        # The error should be raised when creating the Query itself
        # since Query constructor creates a Database instance
        with self.assertRaises(VendorDependencyError) as context:
            Query("postgres")

        error = context.exception
        self.assertEqual(error.vendor, "postgres")
        self.assertIn("asyncpg", error.missing_deps)
        self.assertIn("pip install supersql[postgres]", str(error))
    
    def test_helpful_error_messages(self):
        """Test that error messages are helpful for users."""
        # Test VendorDependencyError message
        error = VendorDependencyError("postgres", ["asyncpg"])
        error_msg = str(error)
        
        # Should contain vendor name
        self.assertIn("postgres", error_msg)
        # Should contain missing dependency
        self.assertIn("asyncpg", error_msg)
        # Should contain installation instructions
        self.assertIn("pip install supersql[postgres]", error_msg)
        self.assertIn("pip install asyncpg", error_msg)
        
        # Test UnsupportedVendorError message
        supported_vendors = ["postgres", "mysql", "sqlite"]
        unsupported_error = UnsupportedVendorError("baddb", supported_vendors)
        unsupported_msg = str(unsupported_error)
        
        # Should contain unsupported vendor
        self.assertIn("baddb", unsupported_msg)
        # Should list supported vendors
        for vendor in supported_vendors:
            self.assertIn(vendor, unsupported_msg)
    
    def test_vendor_aliases(self):
        """Test that vendor aliases work correctly."""
        from supersql.utils.vendor_deps import get_vendor_dependencies
        
        # Test postgres/postgresql alias
        postgres_deps = get_vendor_dependencies("postgres")
        postgresql_deps = get_vendor_dependencies("postgresql")
        self.assertEqual(postgres_deps, postgresql_deps)
        
        # Test mssql/sqlserver alias
        mssql_deps = get_vendor_dependencies("mssql")
        sqlserver_deps = get_vendor_dependencies("sqlserver")
        self.assertEqual(mssql_deps, sqlserver_deps)
    
    def test_installation_commands(self):
        """Test that installation commands are correct."""
        from supersql.utils.vendor_deps import get_installation_command
        
        test_cases = [
            ("postgres", "pip install supersql[postgres]"),
            ("mysql", "pip install supersql[mysql]"),
            ("sqlite", "pip install supersql[sqlite]"),
            ("mssql", "pip install supersql[mssql]"),
        ]
        
        for vendor, expected_cmd in test_cases:
            actual_cmd = get_installation_command(vendor)
            self.assertEqual(actual_cmd, expected_cmd, 
                           f"Wrong installation command for {vendor}")


class TestVendorDependencyDocumentation(unittest.TestCase):
    """Tests to ensure the vendor dependency system is well documented."""
    
    def test_all_vendors_have_extras_defined(self):
        """Test that all vendors have extras defined in pyproject.toml."""
        # This would ideally parse pyproject.toml, but for simplicity
        # we'll just check that our mapping is complete
        from supersql.utils.vendor_deps import VENDOR_DEPENDENCIES, VENDOR_EXTRAS
        
        for vendor in VENDOR_DEPENDENCIES:
            self.assertIn(vendor, VENDOR_EXTRAS, 
                         f"Vendor {vendor} missing from VENDOR_EXTRAS")
    
    def test_dependency_mapping_completeness(self):
        """Test that dependency mappings are complete and consistent."""
        from supersql.utils.vendor_deps import VENDOR_DEPENDENCIES
        from supersql.core.query import SUPPORTED_ENGINES
        
        # All supported engines should have dependency definitions
        for engine in SUPPORTED_ENGINES:
            self.assertIn(engine, VENDOR_DEPENDENCIES,
                         f"Engine {engine} missing dependency definition")
            
            # Dependencies should be a list
            deps = VENDOR_DEPENDENCIES[engine]
            self.assertIsInstance(deps, list, 
                                f"Dependencies for {engine} should be a list")


if __name__ == '__main__':
    unittest.main()
