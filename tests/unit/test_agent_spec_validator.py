#!/usr/bin/env python3
"""
Unit tests for the AgentSpecValidator
"""

import os
import tempfile
import json
import pytest
from unittest.mock import patch

from super_agents.core.agent_spec_validator import AgentSpecValidator


class TestAgentSpecValidator:
    """Test suite for AgentSpecValidator"""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a valid schema file for testing
        schema_path = os.path.join(self.temp_dir, "test_schema.json")
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "title", "mission"],
            "properties": {
                "id": {"type": "string"},  # More permissive for testing custom validation
                "title": {"type": "string"},
                "mission": {"type": "string"},
                "tools": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "capabilities": {
                    "type": "array", 
                    "items": {"type": "string"}
                }
            },
            "additionalProperties": True
        }
        
        with open(schema_path, 'w') as f:
            json.dump(schema, f)
        
        self.schema_path = schema_path

    def teardown_method(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validator_initialization(self):
        """Test that validator initializes correctly"""
        # This test assumes the default schema file exists at the expected location
        # In a real scenario, we'd need the actual schema file to exist
        validator = AgentSpecValidator(self.schema_path)
        assert validator.schema is not None
        assert validator.validator is not None

    def test_validate_valid_spec(self):
        """Test validating a valid agent specification"""
        validator = AgentSpecValidator(self.schema_path)
        
        valid_spec = {
            "id": "test_agent",
            "title": "Test Agent",
            "mission": "Perform test operations",
            "tools": ["tool1", "tool2"],
            "capabilities": ["capability1", "capability2"]
        }
        
        is_valid, errors = validator.validate_spec(valid_spec)
        assert is_valid is True
        assert errors == []

    def test_validate_spec_missing_required_field(self):
        """Test validating a spec with missing required fields"""
        validator = AgentSpecValidator(self.schema_path)
        
        invalid_spec = {
            "id": "test_agent",
            "title": "Test Agent"
            # Missing 'mission' field
        }
        
        is_valid, errors = validator.validate_spec(invalid_spec)
        assert is_valid is False
        assert len(errors) >= 1
        # Check that an error mentions the missing field
        error_found = any("mission" in error.lower() for error in errors)
        assert error_found

    def test_validate_spec_with_duplicate_tools_case_insensitive(self):
        """Test validation detects case-insensitive duplicate tools"""
        validator = AgentSpecValidator(self.schema_path)
        
        spec_with_duplicates = {
            "id": "test_agent",
            "title": "Test Agent", 
            "mission": "Test with duplicate tools",
            "tools": ["Tool1", "tool1", "tool2"],  # Duplicate case-insensitive
            "capabilities": ["cap1", "cap2"]
        }
        
        is_valid, errors = validator.validate_spec(spec_with_duplicates)
        assert is_valid is False
        # Should have error about duplicate tools
        duplicate_error_found = any("duplicate" in error.lower() and "tools" in error.lower() 
                                  for error in errors)
        assert duplicate_error_found

    def test_validate_spec_invalid_id_format(self):
        """Test validation detects invalid ID format"""
        validator = AgentSpecValidator(self.schema_path)
        
        invalid_spec = {
            "id": "InvalidID",  # Should be snake_case
            "title": "Test Agent",
            "mission": "Test with invalid ID"
        }
        
        is_valid, errors = validator.validate_spec(invalid_spec)
        assert is_valid is False
        # Should have error about invalid ID format
        import re
        id_error_found = any(re.search(r"invalid.*id.*format", error.lower()) for error in errors)
        assert id_error_found
    
    def test_validate_spec_custom_validation_passes(self):
        """Test that valid spec passes custom validations"""
        validator = AgentSpecValidator(self.schema_path)
        
        valid_spec = {
            "id": "test_backend_engineer",
            "title": "Test Backend Engineer",
            "mission": "Test backend engineering tasks",
            "tools": ["tool1", "tool2"],
            "capabilities": ["capability1", "capability2"]
        }
        
        is_valid, errors = validator.validate_spec(valid_spec)
        assert is_valid is True

    def test_is_valid_id_format(self):
        """Test the private method for ID format validation"""
        validator = AgentSpecValidator(self.schema_path)
        
        # Valid formats
        assert validator._is_valid_id_format("simple_id") is True
        assert validator._is_valid_id_format("id_with_numbers_123") is True
        assert validator._is_valid_id_format("a") is True  # Minimum valid
        assert validator._is_valid_id_format("a1") is True
        
        # Invalid formats
        assert validator._is_valid_id_format("1starts_with_number") is False
        assert validator._is_valid_id_format("has-CAPS") is False
        assert validator._is_valid_id_format("UPPERCASE") is False
        assert validator._is_valid_id_format("trailing_underscore_") is False
        assert validator._is_valid_id_format("_leading_underscore") is False
        assert validator._is_valid_id_format("") is False

    def test_check_duplicates(self):
        """Test the private method for detecting duplicates"""
        validator = AgentSpecValidator(self.schema_path)
        
        # No duplicates
        no_dupes = ["tool1", "tool2", "TOOL3"]
        errors = validator._check_duplicates(no_dupes, "tools")
        assert len(errors) == 0
        
        # Case-insensitive duplicates
        with_dupes = ["tool1", "Tool1", "tool2"]
        errors = validator._check_duplicates(with_dupes, "tools")
        assert len(errors) == 1
        assert "duplicate" in errors[0].lower()
        assert "tools" in errors[0].lower()