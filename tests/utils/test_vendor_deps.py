import unittest
from unittest.mock import patch, MagicMock
import sys

from supersql.utils.vendor_deps import (
    check_vendor_dependencies,
    validate_vendor_dependencies,
    get_vendor_dependencies,
    is_vendor_supported,
    get_installation_command,
    VendorDependencyError,
    VENDOR_DEPENDENCIES
)


class TestVendorDependencies(unittest.TestCase):
    
    def test_is_vendor_supported(self):
        """Test vendor support checking."""
        # Test supported vendors
        self.assertTrue(is_vendor_supported("postgres"))
        self.assertTrue(is_vendor_supported("mysql"))
        self.assertTrue(is_vendor_supported("sqlite"))
        self.assertTrue(is_vendor_supported("mssql"))
        
        # Test case insensitive
        self.assertTrue(is_vendor_supported("POSTGRES"))
        self.assertTrue(is_vendor_supported("MySQL"))
        
        # Test unsupported vendor
        self.assertFalse(is_vendor_supported("unsupported_db"))
    
    def test_get_vendor_dependencies(self):
        """Test getting vendor dependencies."""
        postgres_deps = get_vendor_dependencies("postgres")
        self.assertEqual(postgres_deps, ["asyncpg"])
        
        mysql_deps = get_vendor_dependencies("mysql")
        self.assertEqual(mysql_deps, ["aiomysql"])
        
        # Test case insensitive
        postgres_deps_upper = get_vendor_dependencies("POSTGRES")
        self.assertEqual(postgres_deps_upper, ["asyncpg"])
        
        # Test unknown vendor
        unknown_deps = get_vendor_dependencies("unknown")
        self.assertEqual(unknown_deps, [])
    
    def test_get_installation_command(self):
        """Test installation command generation."""
        postgres_cmd = get_installation_command("postgres")
        self.assertEqual(postgres_cmd, "pip install supersql[postgres]")
        
        mysql_cmd = get_installation_command("mysql")
        self.assertEqual(mysql_cmd, "pip install supersql[mysql]")
    
    @patch('supersql.utils.vendor_deps.importlib.import_module')
    def test_check_vendor_dependencies_all_installed(self, mock_import):
        """Test when all dependencies are installed."""
        # Mock successful imports
        mock_import.return_value = MagicMock()
        
        all_installed, missing = check_vendor_dependencies("postgres")
        self.assertTrue(all_installed)
        self.assertEqual(missing, [])
        
        # Verify import was called
        mock_import.assert_called_with("asyncpg")
    
    @patch('supersql.utils.vendor_deps.importlib.import_module')
    def test_check_vendor_dependencies_missing(self, mock_import):
        """Test when dependencies are missing."""
        # Mock import failure
        mock_import.side_effect = ImportError("No module named 'asyncpg'")
        
        all_installed, missing = check_vendor_dependencies("postgres")
        self.assertFalse(all_installed)
        self.assertEqual(missing, ["asyncpg"])
    
    @patch('supersql.utils.vendor_deps.importlib.import_module')
    def test_check_vendor_dependencies_partial_missing(self, mock_import):
        """Test when some dependencies are missing."""
        def mock_import_side_effect(module_name):
            if module_name == "aioodbc":
                return MagicMock()
            elif module_name == "pyodbc":
                raise ImportError(f"No module named '{module_name}'")
            else:
                return MagicMock()
        
        mock_import.side_effect = mock_import_side_effect
        
        all_installed, missing = check_vendor_dependencies("mssql")
        self.assertFalse(all_installed)
        self.assertEqual(missing, ["pyodbc"])
    
    def test_check_vendor_dependencies_unknown_vendor(self):
        """Test with unknown vendor."""
        all_installed, missing = check_vendor_dependencies("unknown_vendor")
        self.assertTrue(all_installed)  # No dependencies required
        self.assertEqual(missing, [])
    
    @patch('supersql.utils.vendor_deps.importlib.import_module')
    def test_validate_vendor_dependencies_success(self, mock_import):
        """Test successful validation."""
        mock_import.return_value = MagicMock()
        
        # Should not raise any exception
        try:
            validate_vendor_dependencies("postgres")
        except Exception as e:
            self.fail(f"validate_vendor_dependencies raised {e} unexpectedly!")
    
    @patch('supersql.utils.vendor_deps.importlib.import_module')
    def test_validate_vendor_dependencies_failure(self, mock_import):
        """Test validation failure."""
        mock_import.side_effect = ImportError("No module named 'asyncpg'")
        
        with self.assertRaises(VendorDependencyError) as context:
            validate_vendor_dependencies("postgres")
        
        error = context.exception
        self.assertEqual(error.vendor, "postgres")
        self.assertEqual(error.missing_deps, ["asyncpg"])
        self.assertIn("pip install supersql[postgres]", str(error))
    
    def test_vendor_dependency_error_message(self):
        """Test VendorDependencyError message formatting."""
        error = VendorDependencyError("postgres", ["asyncpg"])
        
        error_msg = str(error)
        self.assertIn("postgres", error_msg)
        self.assertIn("asyncpg", error_msg)
        self.assertIn("pip install supersql[postgres]", error_msg)
        self.assertIn("pip install asyncpg", error_msg)
    
    def test_vendor_dependency_error_custom_message(self):
        """Test VendorDependencyError with custom message."""
        custom_msg = "Custom error message"
        error = VendorDependencyError("postgres", ["asyncpg"], custom_msg)
        
        self.assertEqual(str(error), custom_msg)


if __name__ == '__main__':
    unittest.main()
