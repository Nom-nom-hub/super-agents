#!/usr/bin/env python3
"""
Schema validator for agent specifications
"""

import json
import os
from typing import Any, Dict, List, Tuple

try:
    from jsonschema import Draft7Validator, ValidationError

    JSON_SCHEMA_AVAILABLE = True
except ImportError:
    Draft7Validator = None
    ValidationError = None
    JSON_SCHEMA_AVAILABLE = False


class AgentSpecValidator:
    """Validates agent specifications against defined schemas"""

    def __init__(self, schema_path: str = None):
        """
        Initialize the validator

        Args:
            schema_path: Path to the JSON schema file. If None, uses default.
        """
        if not JSON_SCHEMA_AVAILABLE:
            raise ImportError(
                "jsonschema package is required for validation. "
                "Install with: pip install jsonschema"
            )

        if schema_path is None:
            # Default to the schema in the schemas directory
            current_dir = os.path.dirname(__file__)
            schema_path = os.path.join(
                current_dir, "..", "schemas", "agent_spec_schema.json"
            )
            schema_path = os.path.abspath(schema_path)

        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r") as f:
            self.schema = json.load(f)

        # Compile the validator for better performance
        self.validator = Draft7Validator(self.schema)

    def validate_spec(self, spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate an agent specification against the schema

        Args:
            spec: The agent specification to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        try:
            # Validate against schema
            self.validator.validate(spec)

            # Additional custom validations
            custom_errors = self._custom_validations(spec)
            errors.extend(custom_errors)

        except ValidationError as e:
            # Extract error message
            errors.append(f"Schema validation error: {e.message}")

            # Get more details about where the error occurred
            if e.path:
                path_str = " -> ".join(str(p) for p in e.path)
                errors.append(f"Error location: {path_str}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def _custom_validations(self, spec: Dict[str, Any]) -> List[str]:
        """
        Perform additional custom validations beyond JSON schema

        Args:
            spec: The agent specification to validate

        Returns:
            List of validation errors
        """
        errors = []

        # Check for consistent naming (id should match the filename pattern)
        agent_id = spec.get("id")
        if agent_id:
            # Validate ID format (should be snake_case)
            if not self._is_valid_id_format(agent_id):
                errors.append(
                    f"Invalid ID format: '{agent_id}'. Should be snake_case (lowercase with underscores)."
                )

        # Check that tools and capabilities don't have duplicates when compared case-insensitively
        tools = spec.get("tools", [])
        capabilities = spec.get("capabilities", [])
        inputs = spec.get("inputs", [])
        outputs = spec.get("outputs", [])

        errors.extend(self._check_duplicates(tools, "tools"))
        errors.extend(self._check_duplicates(capabilities, "capabilities"))
        errors.extend(self._check_duplicates(inputs, "inputs"))
        errors.extend(self._check_duplicates(outputs, "outputs"))

        # Check for semantic consistency
        if agent_id and spec.get("title"):
            # The title should be appropriate for the agent ID
            title = spec["title"].lower()
            agent_id_words = agent_id.replace("_", " ").split()
            for word in agent_id_words:
                if word in ["engineer", "agent", "manager"] and word not in title:
                    # This might be too strict, but we can add a warning
                    pass

        return errors

    def _is_valid_id_format(self, agent_id: str) -> bool:
        """
        Check if the agent ID follows the expected format (snake_case)
        """
        import re

        # Must start with lowercase letter
        if not re.match(r"^[a-z]", agent_id):
            return False

        # Must contain only lowercase letters, digits, and underscores
        if not re.match(r"^[a-z][a-z0-9_]*$", agent_id):
            return False

        # Must not end with underscore
        if agent_id.endswith("_"):
            return False

        return True

    def _check_duplicates(self, items: List[str], field_name: str) -> List[str]:
        """
        Check for case-insensitive duplicates in a list
        """
        errors = []
        seen = set()

        for item in items:
            item_lower = item.lower()
            if item_lower in seen:
                errors.append(
                    f"Duplicate {field_name}: '{item}' appears multiple times (case-insensitive)"
                )
            seen.add(item_lower)

        return errors

    def validate_agent_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Validate an agent specification file

        Args:
            file_path: Path to the agent specification YAML/JSON file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        import yaml

        if not os.path.exists(file_path):
            return False, [f"File not found: {file_path}"]

        # Load the file (could be YAML or JSON)
        try:
            if file_path.lower().endswith(".yaml") or file_path.lower().endswith(
                ".yml"
            ):
                with open(file_path, "r") as f:
                    spec = yaml.safe_load(f)
            elif file_path.lower().endswith(".json"):
                with open(file_path, "r") as f:
                    spec = json.load(f)
            else:
                return False, [f"Unsupported file format: {file_path}"]
        except Exception as e:
            return False, [f"Error loading file {file_path}: {str(e)}"]

        if spec is None:
            return False, [f"File {file_path} is empty or contains only comments"]

        return self.validate_spec(spec)

    def validate_all_agent_specs(
        self, agents_dir: str
    ) -> Dict[str, Tuple[bool, List[str]]]:
        """
        Validate all agent specification files in a directory

        Args:
            agents_dir: Directory containing agent specification files

        Returns:
            Dictionary mapping file names to (is_valid, errors) tuples
        """
        results = {}

        for filename in os.listdir(agents_dir):
            if filename.endswith(("_agent.yaml", "_agent.yml", "_agent.json")):
                file_path = os.path.join(agents_dir, filename)
                is_valid, errors = self.validate_agent_file(file_path)
                results[filename] = (is_valid, errors)

        return results


def main():
    """Example usage of the validator"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python agent_spec_validator.py <path_to_agent_spec_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        validator = AgentSpecValidator()
        is_valid, errors = validator.validate_agent_file(file_path)

        if is_valid:
            print(f"✓ {file_path} is valid")
        else:
            print(f"✗ {file_path} is invalid:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
