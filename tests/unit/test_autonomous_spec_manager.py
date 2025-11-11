#!/usr/bin/env python3
"""
Unit tests for AutonomousSpecManager class
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
import yaml

from super_agents.core.autonomous_spec_manager import AutonomousSpecManager, SpecValidator


class TestAutonomousSpecManager:
    """Test suite for AutonomousSpecManager class"""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.manager = AutonomousSpecManager(self.temp_dir)

    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up the temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test AutonomousSpecManager initialization"""
        assert self.manager.agents_dir == self.temp_dir
        assert hasattr(self.manager, 'agents_dir')
        assert hasattr(self.manager, 'history_dir')
        assert os.path.exists(self.manager.history_dir)

    def test_load_agent_spec_file_not_exists(self):
        """Test loading agent spec when file doesn't exist"""
        spec = self.manager.load_agent_spec("nonexistent_agent")
        assert spec == {}

    def test_load_agent_spec_file_exists(self):
        """Test loading agent spec when file exists"""
        # Create agents directory and agent spec file
        agents_dir = os.path.join(self.temp_dir, "agents")
        os.makedirs(agents_dir, exist_ok=True)
        
        spec_data = {
            "id": "test_agent",
            "title": "Test Agent",
            "mission": "Test mission"
        }
        
        spec_path = os.path.join(agents_dir, "test_agent_agent.yaml")
        with open(spec_path, 'w') as f:
            yaml.dump(spec_data, f)
        
        # Create a new manager to point to the temp directory
        manager = AutonomousSpecManager(self.temp_dir)
        spec = manager.load_agent_spec("test_agent")
        
        assert spec["id"] == "test_agent"
        assert spec["title"] == "Test Agent"
        assert spec["mission"] == "Test mission"

    def test_save_agent_spec(self):
        """Test saving agent spec"""
        # Create agents directory
        agents_dir = os.path.join(self.temp_dir, "agents")
        os.makedirs(agents_dir, exist_ok=True)
        
        spec_data = {
            "id": "test_agent",
            "title": "Test Agent",
            "mission": "Test mission"
        }
        
        manager = AutonomousSpecManager(self.temp_dir)
        result = manager.save_agent_spec("test_agent", spec_data)
        
        assert result is True
        
        # Verify file was created with correct content
        spec_path = os.path.join(agents_dir, "test_agent_agent.yaml")
        assert os.path.exists(spec_path)
        
        with open(spec_path, 'r') as f:
            loaded_spec = yaml.safe_load(f)
        
        assert loaded_spec["id"] == "test_agent"
        assert loaded_spec["title"] == "Test Agent"
        assert loaded_spec["mission"] == "Test mission"

    def test_version_spec(self):
        """Test versioning and archiving agent spec"""
        spec_data = {
            "id": "test_agent",
            "title": "Test Agent",
            "mission": "Test mission",
            "version": 5
        }
        
        version_str = self.manager.version_spec("test_agent", spec_data)
        assert version_str == "v5"
        
        # Check that versioned file was created
        versioned_path = os.path.join(
            self.manager.history_dir,
            "test_agent_agent_v5.yaml"
        )
        assert os.path.exists(versioned_path)
        
        # Verify content of versioned file
        with open(versioned_path, 'r') as f:
            saved_spec = yaml.safe_load(f)
        
        assert saved_spec["version"] == 5
        assert saved_spec["title"] == "Test Agent"

    def test_validate_spec_schema_valid(self):
        """Test validating a valid spec schema"""
        valid_spec = {
            "id": "test_agent",
            "title": "Test Agent",
            "mission": "Test mission",
            "tools": ["tool1", "tool2"],
            "capabilities": ["cap1", "cap2"]
        }
        
        is_valid = self.manager._validate_spec_schema(valid_spec)
        assert is_valid is True

    def test_validate_spec_schema_invalid_missing_fields(self):
        """Test validating an invalid spec schema with missing fields"""
        invalid_spec = {
            # Missing required "id" field
            "title": "Test Agent",
            # Missing required "mission" field
        }
        
        is_valid = self.manager._validate_spec_schema(invalid_spec)
        assert is_valid is False

    def test_validate_spec_schema_invalid_wrong_types(self):
        """Test validating a spec with wrong field types"""
        invalid_spec = {
            "id": "test_agent",
            "title": "Test Agent",
            "mission": "Test mission",
            "tools": "should_be_list",  # Wrong type
        }
        
        is_valid = self.manager._validate_spec_schema(invalid_spec)
        assert is_valid is False

    def test_get_spec_history_empty(self):
        """Test getting spec history when no history exists"""
        history = self.manager.get_spec_history("test_agent")
        assert history == []

    def test_get_spec_history_with_versions(self):
        """Test getting spec history with versioned specs"""
        # Create versioned specs
        spec_v1 = {"id": "test_agent", "version": 1, "title": "Test Agent", "last_updated": "2023-01-01T00:00:00"}
        spec_v3 = {"id": "test_agent", "version": 3, "title": "Test Agent", "last_updated": "2023-01-03T00:00:00"}
        
        # Save versioned files
        self.manager.version_spec("test_agent", spec_v1)
        self.manager.version_spec("test_agent", spec_v3)
        
        history = self.manager.get_spec_history("test_agent")
        
        # Should have 2 versions in history
        assert len(history) == 2
        
        # Should be sorted by version number
        assert history[0]["version"] == 1
        assert history[1]["version"] == 3

    def test_compare_specs(self):
        """Test comparing two spec versions"""
        # Create versioned specs
        spec_v1 = {
            "id": "test_agent",
            "version": 1,
            "tools": ["tool1", "tool2"],
            "capabilities": ["cap1", "cap2"],
            "title": "Test Agent"
        }
        spec_v2 = {
            "id": "test_agent",
            "version": 2,
            "tools": ["tool1", "tool2", "tool3"],  # Added tool3
            "capabilities": ["cap1", "cap3"],      # Replaced cap2 with cap3
            "title": "Test Agent"
        }
        
        # Save versioned files
        self.manager.version_spec("test_agent", spec_v1)
        self.manager.version_spec("test_agent", spec_v2)
        
        comparison = self.manager.compare_specs("test_agent", 1, 2)
        
        # Check differences
        assert comparison["version1"] == 1
        assert comparison["version2"] == 2
        assert "tool3" in comparison["tools_added"]
        assert "cap3" in comparison["capabilities_added"]
        assert "cap2" in comparison["capabilities_removed"]

    def test_rollback_spec(self):
        """Test rolling back to a previous spec version"""
        # Create agents directory
        agents_dir = os.path.join(self.temp_dir, "agents")
        os.makedirs(agents_dir, exist_ok=True)
        
        # Create current and previous spec versions
        current_spec = {
            "id": "test_agent",
            "version": 5,
            "title": "Current Agent",
            "mission": "Current mission"
        }
        previous_spec = {
            "id": "test_agent",
            "version": 3,
            "title": "Previous Agent",
            "mission": "Previous mission"
        }
        
        manager = AutonomousSpecManager(self.temp_dir)
        
        # Save both versions (current to agents dir, previous to version history)
        manager.save_agent_spec("test_agent", current_spec)
        manager.version_spec("test_agent", previous_spec)
        
        # Rollback to version 3
        result = manager.rollback_spec("test_agent", 3)
        assert result is True
        
        # Verify the current spec was updated to version 3
        rolled_back_spec = manager.load_agent_spec("test_agent")
        assert rolled_back_spec["title"] == "Previous Agent"
        assert rolled_back_spec["mission"] == "Previous mission"
        # Version should remain 3, not the original version number
        assert rolled_back_spec["version"] == 3

    def test_get_agent_evolution_summary(self):
        """Test getting agent evolution summary"""
        # Create versioned specs
        spec_v1 = {"id": "test_agent", "version": 1, "tools": ["tool1"], "capabilities": ["cap1"], "title": "Test Agent"}
        spec_v2 = {"id": "test_agent", "version": 2, "tools": ["tool1", "tool2"], "capabilities": ["cap1", "cap2"], "title": "Test Agent"}
        
        # Save versioned files
        self.manager.version_spec("test_agent", spec_v1)
        self.manager.version_spec("test_agent", spec_v2)
        
        # Also save current version
        agents_dir = os.path.join(self.temp_dir, "agents")
        os.makedirs(agents_dir, exist_ok=True)
        current_spec = {
            "id": "test_agent",
            "title": "Test Agent",
            "mission": "Test mission",
            "tools": ["tool1", "tool2", "tool3"],
            "capabilities": ["cap1", "cap2", "cap3"],
            "specialization_area": "api_development"
        }
        current_path = os.path.join(agents_dir, "test_agent_agent.yaml")
        with open(current_path, 'w') as f:
            yaml.dump(current_spec, f)
        
        summary = self.manager.get_agent_evolution_summary("test_agent")
        
        assert summary["agent_id"] == "test_agent"
        assert summary["total_versions"] >= 2  # At least 2 versions in history
        # Check tools growth (current has 3, earliest has 1)
        assert summary["evolution"]["tools_growth"] >= 2
        # Check capabilities growth (current has 3, earliest has 1)
        assert summary["evolution"]["capabilities_growth"] >= 2
        assert summary["evolution"]["specialization"] == "api_development"


class TestSpecValidator:
    """Test suite for SpecValidator class"""

    def test_validate_spec_valid(self):
        """Test validating a valid spec"""
        valid_spec = {
            "id": "test_agent",
            "title": "Test Agent",
            "mission": "Test mission",
            "tools": ["tool1", "tool2"],
            "capabilities": ["cap1", "cap2"]
        }
        
        is_valid, message = SpecValidator.validate_spec(valid_spec)
        assert is_valid is True
        assert message == "Valid"

    def test_validate_spec_missing_required_field(self):
        """Test validating a spec with missing required field"""
        invalid_spec = {
            "title": "Test Agent",  # Missing "id"
            "mission": "Test mission"
        }
        
        is_valid, message = SpecValidator.validate_spec(invalid_spec)
        assert is_valid is False
        assert "Missing required field" in message
        assert "id" in message

    def test_validate_spec_wrong_type(self):
        """Test validating a spec with wrong field type"""
        invalid_spec = {
            "id": "test_agent",
            "title": "Test Agent",
            "mission": "Test mission",
            "tools": "should_be_list"  # Wrong type
        }
        
        is_valid, message = SpecValidator.validate_spec(invalid_spec)
        assert is_valid is False
        assert "must be list" in message

    def test_validate_governance_no_issue(self):
        """Test governance validation when no issues"""
        old_spec = {"version": 1}
        new_spec = {"version": 2}
        
        passes, message = SpecValidator.validate_governance(old_spec, new_spec)
        assert passes is True
        assert "Governance check passed" in message

    def test_validate_governance_major_version(self):
        """Test governance validation for major version change"""
        old_spec = {"version": 1}
        new_spec = {"version": 5}  # Big jump
        
        passes, message = SpecValidator.validate_governance(old_spec, new_spec)
        assert passes is False
        assert "Major version change" in message

    def test_validate_governance_too_many_capabilities(self):
        """Test governance validation for too many new capabilities"""
        old_spec = {"capabilities": ["cap1", "cap2"]}
        # Need more than 5 new capabilities (so 6+ new, total 8+)
        new_spec = {"version": 2, "capabilities": ["cap1", "cap2", "cap3", "cap4", "cap5", "cap6", "cap7", "cap8"]}  # 6 new
        
        passes, message = SpecValidator.validate_governance(old_spec, new_spec)
        assert passes is False
        assert "5+ capabilities" in message

    def test_validate_governance_too_many_tools(self):
        """Test governance validation for too many new tools"""
        old_spec = {"tools": ["tool1", "tool2"]}
        # Need more than 8 new tools (so 9+ new, total 11+)
        new_spec = {"version": 2, "tools": ["tool1", "tool2", "tool3", "tool4", "tool5", "tool6", "tool7", "tool8", "tool9", "tool10", "tool11"]}  # 9 new
        
        passes, message = SpecValidator.validate_governance(old_spec, new_spec)
        assert passes is False
        assert "8+ tools" in message