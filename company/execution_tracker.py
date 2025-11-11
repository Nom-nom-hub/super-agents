#!/usr/bin/env python3
"""
Execution Tracker - Captures detailed execution data for learning loops

Records every agent execution with:
- Tools used
- Decisions made
- Blockers encountered
- Performance metrics
- Quality scores
- Time taken

This data feeds the Reflection Agent for autonomous spec regeneration.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ExecutionTracker:
    """Tracks agent executions for autonomous learning"""

    def __init__(self, company_dir: str = "."):
        self.company_dir = company_dir
        self.execution_logs_dir = os.path.join(
            company_dir, "agents", ".execution_logs"
        )
        Path(self.execution_logs_dir).mkdir(parents=True, exist_ok=True)

    def start_execution(self, agent_id: str, task: str) -> str:
        """
        Start tracking an execution

        Args:
            agent_id: ID of the agent executing
            task: Description of the task

        Returns:
            Execution ID for reference
        """
        execution_id = f"exec_{agent_id}_{int(time.time() * 1000)}"

        self.current_execution = {
            "execution_id": execution_id,
            "agent_id": agent_id,
            "task": task,
            "timestamp_start": datetime.now().isoformat(),
            "timestamp_end": None,
            "duration_seconds": 0,
            "status": "in_progress",
            "tools_used": [],
            "decisions_made": [],
            "blockers_encountered": [],
            "outputs_created": [],
            "success_metrics": {
                "test_coverage": None,
                "code_quality_score": None,
                "performance_latency_ms": None,
                "lines_of_code": 0,
            },
            "learnings_extracted": [],
        }

        return execution_id

    def record_tool_usage(self, tool_name: str, context: Optional[str] = None):
        """Record a tool being used during execution"""
        if not hasattr(self, "current_execution"):
            return

        self.current_execution["tools_used"].append(
            {"tool": tool_name, "context": context, "timestamp": datetime.now().isoformat()}
        )

    def record_decision(self, decision: str, rationale: Optional[str] = None):
        """Record a decision made during execution"""
        if not hasattr(self, "current_execution"):
            return

        self.current_execution["decisions_made"].append(
            {"decision": decision, "rationale": rationale, "timestamp": datetime.now().isoformat()}
        )

    def record_blocker(self, blocker: str, resolution: Optional[str] = None):
        """Record a blocker encountered"""
        if not hasattr(self, "current_execution"):
            return

        self.current_execution["blockers_encountered"].append(
            {
                "blocker": blocker,
                "resolution": resolution,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def record_output(self, output_path: str, description: Optional[str] = None):
        """Record an output file created"""
        if not hasattr(self, "current_execution"):
            return

        self.current_execution["outputs_created"].append(
            {
                "path": output_path,
                "description": description,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def record_metrics(self, **kwargs):
        """Record success metrics"""
        if not hasattr(self, "current_execution"):
            return

        for key, value in kwargs.items():
            if key in self.current_execution["success_metrics"]:
                self.current_execution["success_metrics"][key] = value

    def end_execution(self, status: str = "completed", result: Optional[Dict] = None) -> Dict:
        """
        End execution and save log

        Args:
            status: Execution status (completed, failed, partial)
            result: Optional result object

        Returns:
            Complete execution log
        """
        if not hasattr(self, "current_execution"):
            return {}

        self.current_execution["timestamp_end"] = datetime.now().isoformat()
        start_time = datetime.fromisoformat(self.current_execution["timestamp_start"])
        end_time = datetime.fromisoformat(self.current_execution["timestamp_end"])
        self.current_execution["duration_seconds"] = (end_time - start_time).total_seconds()
        self.current_execution["status"] = status

        if result:
            self.current_execution["result"] = result

        # Save to file
        execution_log = self._save_execution_log(self.current_execution)

        return execution_log

    def _save_execution_log(self, execution_data: Dict) -> Dict:
        """Save execution log to file"""
        execution_id = execution_data["execution_id"]
        filepath = os.path.join(self.execution_logs_dir, f"{execution_id}.json")

        with open(filepath, "w") as f:
            json.dump(execution_data, f, indent=2)

        return execution_data

    def get_executions_for_agent(self, agent_id: str) -> List[Dict]:
        """Get all execution logs for an agent"""
        executions = []

        if not os.path.exists(self.execution_logs_dir):
            return executions

        for filename in os.listdir(self.execution_logs_dir):
            if filename.startswith(f"exec_{agent_id}_") and filename.endswith(".json"):
                filepath = os.path.join(self.execution_logs_dir, filename)
                with open(filepath, "r") as f:
                    execution = json.load(f)
                    executions.append(execution)

        # Sort by timestamp
        executions.sort(key=lambda x: x["timestamp_start"], reverse=True)
        return executions

    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get a specific execution log"""
        filepath = os.path.join(self.execution_logs_dir, f"{execution_id}.json")

        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)

        return None

    def get_aggregate_stats(self, agent_id: str) -> Dict:
        """Get aggregate statistics for an agent across all executions"""
        executions = self.get_executions_for_agent(agent_id)

        if not executions:
            return {}

        stats = {
            "total_executions": len(executions),
            "successful_executions": len(
                [e for e in executions if e["status"] == "completed"]
            ),
            "avg_duration_seconds": sum(e["duration_seconds"] for e in executions)
            / len(executions),
            "total_duration_seconds": sum(e["duration_seconds"] for e in executions),
            "tools_frequency": self._count_tool_usage(executions),
            "common_blockers": self._get_common_blockers(executions),
            "avg_test_coverage": self._get_avg_metric(executions, "test_coverage"),
            "avg_code_quality": self._get_avg_metric(executions, "code_quality_score"),
            "avg_latency_ms": self._get_avg_metric(executions, "performance_latency_ms"),
            "total_lines_of_code": sum(
                e["success_metrics"].get("lines_of_code", 0) for e in executions
            ),
        }

        return stats

    def _count_tool_usage(self, executions: List[Dict]) -> Dict[str, int]:
        """Count how often each tool is used"""
        tool_counts = {}

        for execution in executions:
            for tool_entry in execution.get("tools_used", []):
                tool_name = tool_entry.get("tool", "unknown")
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

        return dict(sorted(tool_counts.items(), key=lambda x: x[1], reverse=True))

    def _get_common_blockers(self, executions: List[Dict]) -> List[Dict]:
        """Get most common blockers"""
        blocker_counts = {}

        for execution in executions:
            for blocker_entry in execution.get("blockers_encountered", []):
                blocker = blocker_entry.get("blocker", "unknown")
                blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

        # Sort by frequency
        sorted_blockers = sorted(blocker_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {"blocker": blocker, "frequency": count, "percentage": count / len(executions) * 100}
            for blocker, count in sorted_blockers[:10]
        ]

    def _get_avg_metric(
        self, executions: List[Dict], metric_key: str
    ) -> Optional[float]:
        """Get average of a success metric"""
        values = [
            e["success_metrics"].get(metric_key)
            for e in executions
            if e["success_metrics"].get(metric_key) is not None
        ]

        if not values:
            return None

        return sum(values) / len(values)

    def export_for_reflection(self, agent_id: str) -> Dict:
        """Export execution data in format suitable for reflection agent"""
        executions = self.get_executions_for_agent(agent_id)
        stats = self.get_aggregate_stats(agent_id)

        return {
            "agent_id": agent_id,
            "execution_count": len(executions),
            "successful_count": len([e for e in executions if e["status"] == "completed"]),
            "success_rate": len([e for e in executions if e["status"] == "completed"])
            / len(executions)
            if executions
            else 0,
            "recent_executions": executions[:5],
            "aggregate_stats": stats,
            "all_executions": executions,
        }
