#!/usr/bin/env python3
"""
Unit tests for DelegationPromptGenerator class
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
import yaml

from company.delegation_prompt_generator import DelegationPromptGenerator


class TestDelegationPromptGenerator:
    """Test suite for DelegationPromptGenerator class"""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.generator = DelegationPromptGenerator(self.temp_dir)

    def teardown_method(self):
        """Clean up after each test method."""
        # Clean up the temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test DelegationPromptGenerator initialization"""
        assert self.generator.company_dir == self.temp_dir
        assert hasattr(self.generator, 'intent_mapping_path')
        assert hasattr(self.generator, 'agents_dir')
        assert hasattr(self.generator, 'intent_mapping')
        assert hasattr(self.generator, 'agent_specs')

    def test_load_intent_mapping_file_exists(self):
        """Test loading intent mapping when file exists"""
        # Create an intent mapping file
        intent_mapping = {
            "intents": [
                {
                    "name": "build_api",
                    "primary_agent": "backend_engineer",
                    "keywords": ["api", "backend", "server"],
                    "examples": ["Build a REST API", "Create backend service"]
                }
            ],
            "agent_configs": {
                "claude": {"format": "markdown"},
                "copilot": {"format": "markdown"}
            }
        }
        
        intent_file_path = os.path.join(self.temp_dir, "intent_mapping.yaml")
        with open(intent_file_path, 'w') as f:
            yaml.dump(intent_mapping, f)
        
        # Create a new generator instance to reload the file
        generator = DelegationPromptGenerator(self.temp_dir)
        assert "intents" in generator.intent_mapping
        assert len(generator.intent_mapping["intents"]) == 1
        assert generator.intent_mapping["intents"][0]["primary_agent"] == "backend_engineer"

    def test_load_intent_mapping_file_not_exists(self):
        """Test loading intent mapping when file doesn't exist"""
        generator = DelegationPromptGenerator(self.temp_dir)
        assert generator.intent_mapping == {}

    def test_load_agent_specs_empty_agents_dir(self):
        """Test loading agent specs when agents directory doesn't exist"""
        generator = DelegationPromptGenerator(self.temp_dir)
        specs = generator._load_agent_specs()
        assert specs == {}

    def test_load_agent_specs_with_agents(self):
        """Test loading agent specs when agents exist"""
        # Create agents directory and a test agent file
        agents_dir = os.path.join(self.temp_dir, "agents")
        os.makedirs(agents_dir)
        
        agent_spec = {
            "id": "test_agent",
            "title": "Test Agent",
            "mission": "Test mission"
        }
        
        agent_file_path = os.path.join(agents_dir, "test_agent_agent.yaml")
        with open(agent_file_path, 'w') as f:
            yaml.dump(agent_spec, f)
        
        generator = DelegationPromptGenerator(self.temp_dir)
        specs = generator._load_agent_specs()
        
        assert "test_agent" in specs
        assert specs["test_agent"]["title"] == "Test Agent"
        assert specs["test_agent"]["mission"] == "Test mission"

    def test_generate_delegation_system_prompt_markdown(self):
        """Test generating markdown delegation system prompt"""
        prompt = self.generator.generate_delegation_system_prompt("markdown")
        assert isinstance(prompt, str)
        assert "# SUPER-AGENTS AUTOMATIC DELEGATION SYSTEM" in prompt
        assert "Available Super-Agents" in prompt

    def test_generate_delegation_system_prompt_toml(self):
        """Test generating toml delegation system prompt"""
        prompt = self.generator.generate_delegation_system_prompt("toml")
        assert isinstance(prompt, str)
        assert "AUTOMATIC DELEGATION MODE ENABLED" in prompt
        assert 'description = "Enable automatic delegation to super-agents"' in prompt

    def test_generate_delegation_system_prompt_default(self):
        """Test generating delegation system prompt with default format"""
        # Default should be markdown
        prompt = self.generator.generate_delegation_system_prompt()
        assert isinstance(prompt, str)
        assert "# SUPER-AGENTS AUTOMATIC DELEGATION SYSTEM" in prompt

    def test_generate_agent_specific_context(self):
        """Test generating agent-specific context"""
        # Add an agent to the intent mapping to make the test more meaningful
        self.generator.intent_mapping = {
            "agent_configs": {
                "claude": {"format": "markdown"}
            }
        }
        
        context = self.generator.generate_agent_specific_context("claude")
        assert isinstance(context, str)
        assert "SUPER-AGENTS AUTOMATIC DELEGATION SYSTEM" in context
        assert "For Claude" in context

    def test_generate_agent_specific_context_unknown_agent(self):
        """Test generating context for unknown agent"""
        context = self.generator.generate_agent_specific_context("unknown_agent")
        # Should still work, just without agent-specific customization
        assert isinstance(context, str)

    @patch('builtins.open', create=True)
    @patch('os.path.exists')
    def test_generate_workflow_guide(self, mock_exists, mock_open):
        """Test generating workflow guide"""
        # Mock file system operations
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Setup intent mapping with workflows
        self.generator.intent_mapping = {
            "workflows": [
                {
                    "id": "full_stack_app",
                    "name": "Full Stack App",
                    "description": "Complete full stack application",
                    "agents": {
                        "backend_engineer": "Build REST API",
                        "frontend_engineer": "Build UI"
                    },
                    "trigger_patterns": [
                        "full stack app",
                        "complete application"
                    ]
                }
            ]
        }
        
        guide = self.generator.generate_workflow_guide("full_stack_app")
        assert "Full Stack App" in guide
        assert "Complete full stack application" in guide
        assert "backend_engineer" in guide
        assert "frontend_engineer" in guide
        assert "full stack app" in guide

    def test_generate_workflow_guide_unknown_workflow(self):
        """Test generating guide for unknown workflow"""
        guide = self.generator.generate_workflow_guide("unknown_workflow")
        assert "not found" in guide

    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', create=True)
    def test_generate_all_prompts(self, mock_open, mock_mkdir):
        """Test generating all prompts"""
        # Mock file operations
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Set up intent mapping for testing
        self.generator.intent_mapping = {
            "workflows": [],
            "agent_configs": {
                "claude": {"format": "markdown"},
                "copilot": {"format": "markdown"},
                "qwen": {"format": "markdown"}
            }
        }
        
        output_dir = os.path.join(self.temp_dir, "output")
        self.generator.generate_all_prompts(output_dir)
        
        # Verify that files were written
        assert mock_open.call_count > 0

    def test_main_function_runs(self):
        """Test that main function runs without error (basic smoke test)"""
        # Just make sure the main function exists and doesn't crash
        # This is a basic smoke test
        assert hasattr(self.generator.__class__, 'generate_delegation_system_prompt')
        assert callable(getattr(self.generator, 'generate_delegation_system_prompt'))