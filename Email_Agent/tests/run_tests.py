"""
Main test runner for Customer Discovery Bot test suite.
"""
import sys
import pytest

if __name__ == "__main__":
    # Add current directory to path to allow importing modules
    sys.path.append('/Users/billnewman/Desktop/GitHub/Customer_Discovery_Bot/Email_Agent')
    
    # Run all tests with detailed output
    sys.exit(pytest.main(['-v']))
