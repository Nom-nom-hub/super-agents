#!/usr/bin/env python3
"""
Reflection Agent - Analyzes execution logs to extract learnings

Examines agent execution patterns and generates spec updates:
- Discovers tools that should be added to capabilities
- Identifies patterns in successful executions
- Flags blockers that need addressing
- Extracts new capabilities proven through execution
- Recommends specialization areas

This agent powers autonomous spec regeneration.
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from collections import Counter


class ReflectionAgent:
    """Analyzes executions and generates spec recommendations"""

    def __init__(self, company_dir: str = "."):
        self.company_dir = company_dir

    def analyze_executions(self, agent_id: str, execution_data: Dict) -> Dict:
        """
        Analyze execution data to extract learnings

        Args:
            agent_id: ID of agent to analyze
            execution_data: Data exported from ExecutionTracker

        Returns:
            Learnings with recommendations
        """
        executions = execution_data.get("all_executions", [])
        stats = execution_data.get("aggregate_stats", {})

        if not executions:
            return {
                "agent_id": agent_id,
                "execution_count": 0,
                "learnings": {},
                "recommendations": {},
            }

        learnings = {
            "agent_id": agent_id,
            "execution_count": len(executions),
            "success_rate": execution_data.get("success_rate", 0),
            "tools_discovered": self._discover_tools(executions),
            "patterns_emerged": self._extract_patterns(executions),
            "blockers_to_address": self._analyze_blockers(stats),
            "proven_capabilities": self._extract_proven_capabilities(executions),
            "specialization_area": self._detect_specialization(executions),
            "performance_baseline": self._extract_performance_baseline(stats),
            "quality_metrics": self._extract_quality_metrics(stats),
        }

        return learnings

    def _discover_tools(self, executions: List[Dict]) -> Dict:
        """Discover tools used across executions"""
        all_tools = []

        for execution in executions:
            for tool_entry in execution.get("tools_used", []):
                tool_name = tool_entry.get("tool")
                if tool_name:
                    all_tools.append(tool_name)

        # Count frequency
        tool_counts = Counter(all_tools)

        return {
            "new_tools": list(dict(tool_counts.most_common(10)).keys()),
            "tool_frequencies": dict(tool_counts.most_common(10)),
            "confidence_by_frequency": {
                tool: min(count / len(executions), 1.0)
                for tool, count in tool_counts.most_common(10)
            },
        }

    def _extract_patterns(self, executions: List[Dict]) -> List[Dict]:
        """Extract successful patterns from executions"""
        patterns = []

        # Find most common decision combinations
        decision_combinations = {}

        for execution in executions:
            if execution["status"] == "completed":
                decisions = tuple(sorted([d["decision"] for d in execution.get("decisions_made", [])]))
                if decisions:
                    decision_combinations[decisions] = decision_combinations.get(decisions, 0) + 1

        # Get top patterns
        sorted_patterns = sorted(
            decision_combinations.items(), key=lambda x: x[1], reverse=True
        )

        for pattern, frequency in sorted_patterns[:5]:
            patterns.append(
                {
                    "pattern": list(pattern),
                    "frequency": frequency,
                    "success_rate": frequency / len(executions),
                    "recommendation": f"This pattern appears in {frequency} executions. Consider codifying it.",
                }
            )

        return patterns

    def _analyze_blockers(self, stats: Dict) -> List[Dict]:
        """Analyze blockers to identify improvement areas"""
        common_blockers = stats.get("common_blockers", [])

        recommendations = []

        for blocker_info in common_blockers[:5]:
            blocker = blocker_info.get("blocker", "")
            frequency = blocker_info.get("frequency", 0)
            percentage = blocker_info.get("percentage", 0)

            recommendations.append(
                {
                    "blocker": blocker,
                    "frequency": frequency,
                    "percentage": round(percentage, 1),
                    "severity": (
                        "critical"
                        if percentage > 50
                        else "high"
                        if percentage > 25
                        else "medium"
                    ),
                    "action": self._suggest_blocker_action(blocker),
                }
            )

        return recommendations

    def _suggest_blocker_action(self, blocker: str) -> str:
        """Suggest action for a blocker"""
        blocker_lower = blocker.lower()

        if "research" in blocker_lower or "investigate" in blocker_lower:
            return "Add knowledge base documentation"
        elif "config" in blocker_lower or "setup" in blocker_lower:
            return "Create configuration template"
        elif "test" in blocker_lower:
            return "Add test utilities or fixtures"
        elif "performance" in blocker_lower:
            return "Profile and optimize"
        elif "integration" in blocker_lower:
            return "Create integration helper"
        else:
            return "Document solution and create guide"

    def _extract_proven_capabilities(self, executions: List[Dict]) -> List[str]:
        """Extract capabilities proven by successful executions"""
        capabilities = set()

        for execution in executions:
            if execution["status"] == "completed":
                # Infer from decisions and tools
                for decision in execution.get("decisions_made", []):
                    decision_text = decision.get("decision", "")
                    if decision_text:
                        # Parse capability from decision
                        capability = self._extract_capability_from_decision(decision_text)
                        if capability:
                            capabilities.add(capability)

        return list(sorted(capabilities))

    def _extract_capability_from_decision(self, decision: str) -> Optional[str]:
        """Extract capability from a decision statement"""
        # Simple heuristic: capitalize and clean up decision
        words = decision.lower().split()

        # Remove common words
        stop_words = {"used", "implemented", "added", "created", "the", "a", "an", "for"}
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]

        if meaningful_words:
            # Create capability from key words
            capability = " ".join(meaningful_words[:3]).title()
            return capability

        return None

    def _detect_specialization(self, executions: List[Dict]) -> Optional[str]:
        """Detect if agent is specializing in a particular area"""
        if not executions:
            return None

        # Analyze task descriptions for common themes
        task_keywords = []

        for execution in executions:
            task = execution.get("task", "").lower()
            task_keywords.extend(task.split())

        # Find most common keywords
        keyword_counts = Counter(task_keywords)
        common_keywords = [kw for kw, count in keyword_counts.most_common(5) if count > 1]

        if len(common_keywords) >= 2:
            specialization = " ".join(common_keywords).title()
            return specialization

        return None

    def _extract_performance_baseline(self, stats: Dict) -> Dict:
        """Extract performance metrics"""
        return {
            "avg_duration_seconds": round(stats.get("avg_duration_seconds", 0), 2),
            "total_duration_seconds": round(stats.get("total_duration_seconds", 0), 2),
            "avg_test_coverage": round(stats.get("avg_test_coverage", 0), 1) if stats.get("avg_test_coverage") else None,
            "avg_code_quality": round(stats.get("avg_code_quality", 0), 1) if stats.get("avg_code_quality") else None,
            "avg_latency_ms": round(stats.get("avg_latency_ms", 0), 1) if stats.get("avg_latency_ms") else None,
            "total_lines_of_code": stats.get("total_lines_of_code", 0),
        }

    def _extract_quality_metrics(self, stats: Dict) -> Dict:
        """Extract quality and productivity metrics"""
        total = stats.get("total_executions", 1)
        successful = stats.get("successful_executions", 0)

        return {
            "success_rate": round(successful / total * 100, 1) if total > 0 else 0,
            "execution_count": total,
            "avg_lines_per_execution": round(
                stats.get("total_lines_of_code", 0) / total, 0
            ) if total > 0 else 0,
        }

    def generate_spec_update(
        self, current_spec: Dict, learnings: Dict
    ) -> Dict:
        """
        Generate updated spec based on learnings

        Args:
            current_spec: Current agent YAML spec
            learnings: Learnings from analysis

        Returns:
            Updated spec with new discoveries
        """
        updated_spec = current_spec.copy()

        # Update tools
        if learnings.get("tools_discovered"):
            current_tools = set(updated_spec.get("tools", []))
            new_tools = set(learnings["tools_discovered"].get("new_tools", []))
            updated_spec["tools"] = list(sorted(current_tools | new_tools))

        # Update capabilities
        if learnings.get("proven_capabilities"):
            current_capabilities = set(updated_spec.get("capabilities", []))
            proven = set(learnings.get("proven_capabilities", []))
            updated_spec["capabilities"] = list(sorted(current_capabilities | proven))

        # Add performance baseline
        if learnings.get("performance_baseline"):
            updated_spec["performance_baseline"] = learnings["performance_baseline"]

        # Add patterns learned
        if learnings.get("patterns_emerged"):
            updated_spec["patterns_learned"] = [p["pattern"] for p in learnings["patterns_emerged"]]

        # Add known blockers
        if learnings.get("blockers_to_address"):
            updated_spec["known_blockers"] = [
                b["blocker"] for b in learnings["blockers_to_address"]
            ]

        # Add specialization if detected
        if learnings.get("specialization_area"):
            updated_spec["specialization_area"] = learnings["specialization_area"]

        # Add quality metrics
        if learnings.get("quality_metrics"):
            updated_spec["quality_metrics"] = learnings["quality_metrics"]

        # Increment version
        updated_spec["version"] = updated_spec.get("version", 1) + 1
        updated_spec["last_updated"] = self._get_timestamp()
        updated_spec["iterations_to_learn"] = learnings.get("execution_count", 0)

        return updated_spec

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def validate_spec_changes(
        self, old_spec: Dict, new_spec: Dict
    ) -> Dict:
        """
        Validate spec changes for governance

        Args:
            old_spec: Previous spec
            new_spec: Updated spec

        Returns:
            Validation result with flags
        """
        changes = {
            "tools_added": list(
                set(new_spec.get("tools", []))
                - set(old_spec.get("tools", []))
            ),
            "capabilities_added": list(
                set(new_spec.get("capabilities", []))
                - set(old_spec.get("capabilities", []))
            ),
            "version_increment": new_spec.get("version", 1) - old_spec.get("version", 1),
            "requires_review": False,
            "review_reason": None,
        }

        # Governance: Require review for major changes
        if changes["version_increment"] >= 3:
            changes["requires_review"] = True
            changes["review_reason"] = "Major version change (3+ versions)"
        elif len(changes["capabilities_added"]) > 5:
            changes["requires_review"] = True
            changes["review_reason"] = "Adding 5+ new capabilities"
        elif len(changes["tools_added"]) > 8:
            changes["requires_review"] = True
            changes["review_reason"] = "Adding 8+ new tools"

        changes["change_summary"] = (
            f"+{len(changes['tools_added'])} tools, "
            f"+{len(changes['capabilities_added'])} capabilities"
        )

        return changes

    def create_learning_report(
        self, agent_id: str, learnings: Dict, changes: Dict
    ) -> str:
        """
        Create human-readable learning report

        Args:
            agent_id: Agent being reported on
            learnings: Learnings extracted
            changes: Changes made

        Returns:
            Markdown report
        """
        report = f"""# Learning Report: {agent_id}

Generated: {self._get_timestamp()}

## Summary

- **Executions Analyzed**: {learnings.get('execution_count', 0)}
- **Success Rate**: {learnings.get('success_rate', 0) * 100:.1f}%
- **Specialization**: {learnings.get('specialization_area', 'Generalist')}

## Discoveries

### New Tools
{self._format_list(learnings.get('tools_discovered', {}).get('new_tools', []))}

### New Capabilities
{self._format_list(learnings.get('proven_capabilities', []))}

### Patterns Emerged
"""

        for pattern in learnings.get("patterns_emerged", []):
            report += f"- {', '.join(pattern['pattern'])}\n"

        report += f"\n## Performance Baseline\n\n"
        perf = learnings.get("performance_baseline", {})
        report += f"- Avg Duration: {perf.get('avg_duration_seconds', 0):.1f}s\n"
        report += f"- Avg Test Coverage: {perf.get('avg_test_coverage', 0)}%\n"
        report += f"- Avg Code Quality: {perf.get('avg_code_quality', 0)}/10\n"

        report += f"\n## Blockers to Address\n\n"
        for blocker in learnings.get("blockers_to_address", []):
            report += f"- **{blocker['blocker']}** ({blocker['percentage']:.1f}%): {blocker['action']}\n"

        report += f"\n## Changes Made\n\n"
        report += f"- {changes['change_summary']}\n"
        report += f"- Requires Review: {'Yes' if changes['requires_review'] else 'No'}\n"
        if changes["requires_review"]:
            report += f"- Review Reason: {changes['review_reason']}\n"

        return report

    def _format_list(self, items: List[str]) -> str:
        """Format list for markdown"""
        if not items:
            return "None discovered"
        return "\n".join([f"- {item}" for item in items])
