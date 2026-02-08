import unittest
from unittest.mock import patch, MagicMock

from supersql.core.database import Database, UnknownDriverException
from supersql.errors import VendorDependencyError, UnsupportedVendorError
from supersql.core.query import Query


class TestDatabaseVendorDependencies(unittest.TestCase):
    
    def test_runtime_module_resolver_unsupported_vendor(self):
        """Test runtime_module_resolver with unsupported vendor."""
        with self.assertRaises(UnsupportedVendorError) as context:
            Database.runtime_module_resolver("unsupported_vendor")
        
        error = context.exception
        self.assertEqual(error.vendor, "unsupported_vendor")
        self.assertIsInstance(error.supported_vendors, list)
        self.assertIn("postgres", error.supported_vendors)
    
    @patch('supersql.core.database.import_module')
    def test_runtime_module_resolver_successful_import(self, mock_import):
        """Test successful module import."""
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        
        result = Database.runtime_module_resolver("postgres")
        
        self.assertEqual(result, mock_module)
        mock_import.assert_called_once_with("supersql.engines.postgres")
    
    @patch('supersql.core.database.import_module')
    def test_runtime_module_resolver_vendor_dependency_error(self, mock_import):
        """Test handling of VendorDependencyError."""
        vendor_error = VendorDependencyError("postgres", ["asyncpg"])
        mock_import.side_effect = vendor_error
        
        with self.assertRaises(VendorDependencyError) as context:
            Database.runtime_module_resolver("postgres")
        
        # Should re-raise the same error
        self.assertEqual(context.exception, vendor_error)
    
    @patch('supersql.core.database.import_module')
    def test_runtime_module_resolver_missing_dependency_import_error(self, mock_import):
        """Test handling of ImportError for missing dependencies."""
        # Simulate ImportError mentioning a known dependency
        import_error = ImportError("No module named 'asyncpg'")
        mock_import.side_effect = import_error
        
        with self.assertRaises(VendorDependencyError) as context:
            Database.runtime_module_resolver("postgres")
        
        error = context.exception
        self.assertEqual(error.vendor, "postgres")
        self.assertEqual(error.missing_deps, ["asyncpg"])
        self.assertIn("pip install supersql[postgres]", str(error))
    
    @patch('supersql.core.database.import_module')
    def test_runtime_module_resolver_other_import_error(self, mock_import):
        """Test handling of other ImportErrors."""
        # Simulate ImportError not related to dependencies
        import_error = ImportError("Some other import error")
        import_error.name = "postgres"  # Set name attribute
        mock_import.side_effect = import_error
        
        with self.assertRaises(UnknownDriverException) as context:
            Database.runtime_module_resolver("postgres")
        
        self.assertIn("Could not resolve postgres into a DB driver", str(context.exception))
    
    @patch('supersql.core.database.import_module')
    def test_runtime_module_resolver_import_error_different_name(self, mock_import):
        """Test ImportError with different name attribute."""
        import_error = ImportError("Some import error")
        import_error.name = "other_module"  # Different from requested module
        mock_import.side_effect = import_error
        
        with self.assertRaises(ImportError) as context:
            Database.runtime_module_resolver("postgres")
        
        # Should re-raise the original ImportError
        self.assertEqual(context.exception, import_error)
    
    @patch('supersql.core.database.Database.runtime_module_resolver')
    def test_database_init_with_vendor_dependency_error(self, mock_resolver):
        """Test Database initialization with vendor dependency error."""
        vendor_error = VendorDependencyError("mysql", ["aiomysql"])
        mock_resolver.side_effect = vendor_error
        
        # Create a mock query
        mock_query = MagicMock()
        mock_query._engine = "mysql"
        
        with self.assertRaises(VendorDependencyError) as context:
            Database(mock_query)
        
        self.assertEqual(context.exception, vendor_error)
    
    @patch('supersql.core.database.Database.runtime_module_resolver')
    def test_database_init_with_unsupported_vendor_error(self, mock_resolver):
        """Test Database initialization with unsupported vendor error."""
        unsupported_error = UnsupportedVendorError("unsupported_db", ["postgres", "mysql"])
        mock_resolver.side_effect = unsupported_error
        
        # Create a mock query
        mock_query = MagicMock()
        mock_query._engine = "unsupported_db"
        
        with self.assertRaises(UnsupportedVendorError) as context:
            Database(mock_query)
        
        self.assertEqual(context.exception, unsupported_error)


class TestDatabaseVendorDependenciesIntegration(unittest.TestCase):
    """Integration tests that test the full flow."""
    
    def test_query_with_unsupported_vendor(self):
        """Test Query creation with unsupported vendor."""
        with self.assertRaises(NotImplementedError) as context:
            Query("unsupported_vendor")
        
        self.assertIn("unsupported_vendor is not a supersql supported engine", str(context.exception))
    



if __name__ == '__main__':
    unittest.main()
