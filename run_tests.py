#!/usr/bin/env python
"""
SpottEd Test Runner
Runs all unit and integration tests with coverage report
"""
import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests():
    """Run all tests and generate report"""
    print("=" * 60)
    print("SpottEd Test Suite")
    print("=" * 60)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load tests from test directory
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    # Add all test modules
    for test_file in ['test_models', 'test_services', 'test_integration']:
        try:
            tests = loader.loadTestsFromName(f'tests.{test_file}')
            suite.addTests(tests)
            print(f"✓ Loaded {test_file}")
        except Exception as e:
            print(f"✗ Failed to load {test_file}: {e}")
    
    print("\n" + "=" * 60)
    print("Running Tests...")
    print("=" * 60 + "\n")
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) 
                    / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())







