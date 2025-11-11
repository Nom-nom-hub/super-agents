#!/usr/bin/env python3
"""
Autonomous Spec Manager - Manages spec versioning and regeneration

Handles:
- Loading current agent specs
- Versioning and history tracking
- Schema validation
- Spec updates with governance
- Intent mapping updates
- Broadcasting to external systems

Completes the feedback loop: execute → reflect → update → validate → next execution
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml


class AutonomousSpecManager:
    """Manages autonomous spec regeneration and versioning"""

    def __init__(self, company_dir: str = "."):
        self.company_dir = company_dir
        self.agents_dir = os.path.join(company_dir, "agents")
        self.history_dir = os.path.join(self.agents_dir, ".history")
        self.intent_mapping_path = os.path.join(company_dir, "intent_mapping.yaml")

        # Ensure directories exist
        Path(self.history_dir).mkdir(parents=True, exist_ok=True)

    def load_agent_spec(self, agent_id: str) -> Dict:
        """Load current agent spec"""
        spec_path = os.path.join(self.agents_dir, f"{agent_id}_agent.yaml")

        if not os.path.exists(spec_path):
            return {}

        with open(spec_path, "r") as f:
            return yaml.safe_load(f) or {}

    def save_agent_spec(self, agent_id: str, spec: Dict, validate: bool = True) -> bool:
        """
        Save updated agent spec

        Args:
            agent_id: Agent ID
            spec: Updated spec
            validate: Whether to validate schema

        Returns:
            True if successful
        """
        if validate:
            if not self._validate_spec_schema(spec):
                print(f"❌ Spec validation failed for {agent_id}")
                return False

        spec_path = os.path.join(self.agents_dir, f"{agent_id}_agent.yaml")

        with open(spec_path, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        return True

    def version_spec(self, agent_id: str, spec: Dict) -> str:
        """
        Version and archive current spec

        Args:
            agent_id: Agent ID
            spec: Spec to archive

        Returns:
            Version string (e.g., "v5")
        """
        current_version = spec.get("version", 1)
        version_str = f"v{current_version}"

        # Create versioned filename
        versioned_path = os.path.join(
            self.history_dir, f"{agent_id}_agent_{version_str}.yaml"
        )

        # Archive previous version
        with open(versioned_path, "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        return version_str

    def regenerate_spec(
        self, agent_id: str, learnings: Dict, changes: Dict, reflection_agent_obj
    ) -> Tuple[bool, Dict, Optional[str]]:
        """
        Full spec regeneration cycle

        Args:
            agent_id: Agent ID
            learnings: Learnings from reflection
            changes: Changes from validation
            reflection_agent_obj: ReflectionAgent instance

        Returns:
            (success, updated_spec, governance_note)
        """
        # Load current spec
        current_spec = self.load_agent_spec(agent_id)
        if not current_spec:
            return False, {}, "Agent spec not found"

        # Generate updated spec
        updated_spec = reflection_agent_obj.generate_spec_update(
            current_spec, learnings
        )

        # Validate changes
        change_validation = reflection_agent_obj.validate_spec_changes(
            current_spec, updated_spec
        )

        governance_note = None

        # Check governance requirements
        if change_validation["requires_review"]:
            governance_note = f"⚠ Review Required: {change_validation['review_reason']}"
            print(governance_note)
            # Could implement approval flow here
            # For now, allow update but flag it

        # Version current spec before updating
        self.version_spec(agent_id, current_spec)

        # Save updated spec
        if not self.save_agent_spec(agent_id, updated_spec, validate=True):
            return False, {}, "Spec save failed"

        # Create learning report
        report = reflection_agent_obj.create_learning_report(
            agent_id, learnings, change_validation
        )

        # Save report
        self._save_learning_report(agent_id, report)

        # Update intent mappings if new specialization detected
        if learnings.get("specialization_area"):
            self._update_intent_mappings(agent_id, learnings)

        return True, updated_spec, governance_note

    def _validate_spec_schema(self, spec: Dict) -> bool:
        """Validate spec against required schema"""
        required_fields = {
            "id": str,
            "title": str,
            "mission": str,
        }

        for field, field_type in required_fields.items():
            if field not in spec or not isinstance(spec[field], field_type):
                print(f"❌ Schema validation failed: Missing or invalid '{field}'")
                return False

        # Validate optional fields have correct types
        optional_validations = {
            "tools": list,
            "capabilities": list,
            "patterns_learned": list,
            "known_blockers": list,
            "performance_baseline": dict,
            "quality_metrics": dict,
        }

        for field, expected_type in optional_validations.items():
            if field in spec and not isinstance(spec[field], expected_type):
                print(
                    f"❌ Schema validation failed: '{field}' must be {expected_type.__name__}"
                )
                return False

        return True

    def _save_learning_report(self, agent_id: str, report: str):
        """Save learning report to file"""
        reports_dir = os.path.join(self.agents_dir, ".learning_reports")
        Path(reports_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(reports_dir, f"{agent_id}_{timestamp}.md")

        with open(report_path, "w") as f:
            f.write(report)

    def _update_intent_mappings(self, agent_id: str, learnings: Dict):
        """
        Update intent_mapping.yaml with new specializations

        Args:
            agent_id: Agent that developed specialization
            learnings: Learnings including specialization
        """
        if not os.path.exists(self.intent_mapping_path):
            return

        with open(self.intent_mapping_path, "r") as f:
            intent_mapping = yaml.safe_load(f) or {}

        specialization = learnings.get("specialization_area")
        if not specialization:
            return

        # Create sub-specialization entry
        if "intents" not in intent_mapping:
            intent_mapping["intents"] = []

        # Check if we should add sub-specialization

        # Add to sub_specializations of relevant intent
        found = False
        for intent in intent_mapping.get("intents", []):
            if agent_id in intent.get("primary_agent", "") or agent_id in intent.get(
                "supporting_agents", []
            ):
                if "sub_specializations" not in intent:
                    intent["sub_specializations"] = []

                # Check if not already there
                if not any(
                    s.get("agent") == agent_id
                    and s.get("specialization") == specialization
                    for s in intent["sub_specializations"]
                ):
                    intent["sub_specializations"].append(
                        {
                            "specialization": specialization,
                            "agent": agent_id,
                            "confidence": learnings.get("success_rate", 0.8),
                            "execution_count": learnings.get("execution_count", 0),
                        }
                    )
                    found = True

        if found:
            with open(self.intent_mapping_path, "w") as f:
                yaml.dump(intent_mapping, f, default_flow_style=False, sort_keys=False)

    def get_spec_history(self, agent_id: str) -> list:
        """Get version history for an agent"""
        versions = []

        for filename in sorted(os.listdir(self.history_dir)):
            if filename.startswith(f"{agent_id}_agent_v") and filename.endswith(
                ".yaml"
            ):
                version_path = os.path.join(self.history_dir, filename)
                with open(version_path, "r") as f:
                    spec = yaml.safe_load(f)
                    versions.append(
                        {
                            "version": spec.get("version"),
                            "filename": filename,
                            "timestamp": spec.get("last_updated"),
                            "tools_count": len(spec.get("tools", [])),
                            "capabilities_count": len(spec.get("capabilities", [])),
                        }
                    )

        return versions

    def compare_specs(self, agent_id: str, version1: int, version2: int) -> Dict:
        """Compare two versions of a spec"""

        def load_version(version):
            path = os.path.join(self.history_dir, f"{agent_id}_agent_v{version}.yaml")
            if os.path.exists(path):
                with open(path, "r") as f:
                    return yaml.safe_load(f)
            return {}

        spec1 = load_version(version1)
        spec2 = load_version(version2)

        return {
            "version1": version1,
            "version2": version2,
            "tools_added": list(
                set(spec2.get("tools", [])) - set(spec1.get("tools", []))
            ),
            "tools_removed": list(
                set(spec1.get("tools", [])) - set(spec2.get("tools", []))
            ),
            "capabilities_added": list(
                set(spec2.get("capabilities", [])) - set(spec1.get("capabilities", []))
            ),
            "capabilities_removed": list(
                set(spec1.get("capabilities", [])) - set(spec2.get("capabilities", []))
            ),
        }

    def rollback_spec(self, agent_id: str, target_version: int) -> bool:
        """
        Rollback agent spec to previous version

        Args:
            agent_id: Agent ID
            target_version: Version to rollback to

        Returns:
            True if successful
        """
        version_path = os.path.join(
            self.history_dir, f"{agent_id}_agent_v{target_version}.yaml"
        )

        if not os.path.exists(version_path):
            print(f"❌ Version {target_version} not found")
            return False

        with open(version_path, "r") as f:
            spec = yaml.safe_load(f)

        # Save current version to history first
        current_spec = self.load_agent_spec(agent_id)
        if current_spec:
            self.version_spec(agent_id, current_spec)

        # Restore old version
        if self.save_agent_spec(agent_id, spec, validate=True):
            print(f"✓ Rolled back {agent_id} to v{target_version}")
            return True

        return False

    def get_agent_evolution_summary(self, agent_id: str) -> Dict:
        """Get summary of agent's evolution"""
        history = self.get_spec_history(agent_id)
        current_spec = self.load_agent_spec(agent_id)

        if not history:
            return {}

        earliest = history[0] if history else {}
        latest = current_spec

        summary = {
            "agent_id": agent_id,
            "total_versions": len(history),
            "versions": history,
            "evolution": {
                "tools_growth": len(latest.get("tools", []))
                - len(earliest.get("tools", [])),
                "capabilities_growth": len(latest.get("capabilities", []))
                - len(earliest.get("capabilities", [])),
                "specialization": latest.get("specialization_area", "None"),
                "quality_improvement": {
                    "success_rate": latest.get("quality_metrics", {}).get(
                        "success_rate"
                    ),
                    "avg_code_quality": latest.get("performance_baseline", {}).get(
                        "avg_code_quality"
                    ),
                    "avg_test_coverage": latest.get("performance_baseline", {}).get(
                        "avg_test_coverage"
                    ),
                },
            },
        }

        return summary


class SpecValidator:
    """Validates specs against schema and governance policies"""

    REQUIRED_FIELDS = {"id", "title", "mission"}
    OPTIONAL_FIELDS = {
        "tools",
        "capabilities",
        "patterns_learned",
        "known_blockers",
        "performance_baseline",
        "quality_metrics",
        "specialization_area",
        "version",
        "last_updated",
    }

    @staticmethod
    def validate_spec(spec: Dict) -> Tuple[bool, str]:
        """
        Validate spec structure

        Args:
            spec: Spec to validate

        Returns:
            (is_valid, message)
        """
        # Check required fields
        for field in SpecValidator.REQUIRED_FIELDS:
            if field not in spec:
                return False, f"Missing required field: {field}"

        # Check field types
        type_checks = {
            "tools": list,
            "capabilities": list,
            "patterns_learned": list,
            "known_blockers": list,
            "performance_baseline": dict,
            "quality_metrics": dict,
        }

        for field, expected_type in type_checks.items():
            if field in spec and not isinstance(spec[field], expected_type):
                return False, f"Field '{field}' must be {expected_type.__name__}"

        return True, "Valid"

    @staticmethod
    def validate_governance(old_spec: Dict, new_spec: Dict) -> Tuple[bool, str]:
        """
        Check governance requirements

        Args:
            old_spec: Previous spec
            new_spec: Updated spec

        Returns:
            (passes_governance, message)
        """
        version_diff = new_spec.get("version", 1) - old_spec.get("version", 1)

        if version_diff >= 3:
            return False, "Major version change requires review"

        new_capabilities = len(new_spec.get("capabilities", [])) - len(
            old_spec.get("capabilities", [])
        )
        if new_capabilities > 5:
            return False, "Adding 5+ capabilities requires review"

        new_tools = len(new_spec.get("tools", [])) - len(old_spec.get("tools", []))
        if new_tools > 8:
            return False, "Adding 8+ tools requires review"

        return True, "Governance check passed"
