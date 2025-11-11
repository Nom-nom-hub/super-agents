#!/usr/bin/env python3
"""
Autonomous Learning Integration Module

Provides pre-execution and post-execution hooks for agent task execution.
Integrates with ExecutionTracker, ReflectionAgent, and AutonomousSpecManager
to enable autonomous spec regeneration.

This module can be used by:
- Agent orchestrators
- External agent runners (Claude, Copilot, etc.)
- CLI tools
- REST API handlers

Usage:
    learning = LearningIntegration(company_dir)
    
    # Pre-execution
    exec_id = learning.pre_execute(agent_id, task_description)
    
    # Track during execution
    learning.track_tool(tool_name, context)
    learning.track_decision(decision, rationale)
    learning.track_blocker(blocker, resolution)
    learning.track_output(file_path, description)
    
    # Post-execution with automatic learning
    result = learning.post_execute(agent_id, status="completed", metrics={...})
"""

import os
from typing import Dict, Optional, Any
from datetime import datetime

try:
    from agent_support import AgentSupport
    HAS_AGENT_SUPPORT = True
except ImportError:
    HAS_AGENT_SUPPORT = False
    AgentSupport = None


class LearningIntegration:
    """Integration point for autonomous learning in agent execution"""

    def __init__(self, company_dir: str = "."):
        """
        Initialize learning integration
        
        Args:
            company_dir: Path to company directory
        """
        self.company_dir = company_dir
        self.agent_support = None
        self.current_exec_id = None
        
        if HAS_AGENT_SUPPORT:
            try:
                self.agent_support = AgentSupport(company_dir)
            except Exception as e:
                print(f"⚠ Learning integration unavailable: {e}")

    def is_available(self) -> bool:
        """Check if learning system is available"""
        return self.agent_support is not None

    def pre_execute(self, agent_id: str, task_description: str) -> Optional[str]:
        """
        Pre-execution hook: Start tracking an agent execution
        
        Call this before agent task execution starts.
        
        Args:
            agent_id: ID of agent executing task
            task_description: Description of the task
            
        Returns:
            Execution ID, or None if learning unavailable
            
        Example:
            exec_id = learning.pre_execute("backend_engineer", "Design REST API")
        """
        if not self.agent_support:
            return None
        
        try:
            self.current_exec_id = self.agent_support.track_execution_start(
                agent_id, task_description
            )
            print(f"[Learning] Started tracking execution: {self.current_exec_id}")
            return self.current_exec_id
        except Exception as e:
            print(f"❌ Error in pre_execute: {e}")
            return None

    def track_tool(self, tool_name: str, context: Optional[str] = None):
        """
        Track tool usage during execution
        
        Args:
            tool_name: Name of tool/capability used
            context: Optional context about how it was used
            
        Example:
            learning.track_tool("FastAPI", "Used for REST API implementation")
        """
        if not self.agent_support:
            return
        
        try:
            self.agent_support.track_execution_tool(tool_name, context)
        except Exception as e:
            print(f"❌ Error tracking tool: {e}")

    def track_decision(self, decision: str, rationale: Optional[str] = None):
        """
        Track a decision made during execution
        
        Args:
            decision: Description of decision
            rationale: Why this decision was made
            
        Example:
            learning.track_decision(
                "Use async/await for I/O",
                "Better performance for concurrent requests"
            )
        """
        if not self.agent_support:
            return
        
        try:
            self.agent_support.track_execution_decision(decision, rationale)
        except Exception as e:
            print(f"❌ Error tracking decision: {e}")

    def track_blocker(self, blocker: str, resolution: Optional[str] = None):
        """
        Track a blocker encountered during execution
        
        Args:
            blocker: Description of the blocker
            resolution: How it was resolved or workaround
            
        Example:
            learning.track_blocker(
                "Connection pool sizing",
                "Researched best practices and implemented"
            )
        """
        if not self.agent_support:
            return
        
        try:
            self.agent_support.track_execution_blocker(blocker, resolution)
        except Exception as e:
            print(f"❌ Error tracking blocker: {e}")

    def track_output(self, output_path: str, description: Optional[str] = None):
        """
        Track output files/artifacts created
        
        Args:
            output_path: Path or name of output
            description: Description of the output
            
        Example:
            learning.track_output("api/main.py", "Main API implementation")
        """
        if not self.agent_support:
            return
        
        try:
            self.agent_support.track_execution_output(output_path, description)
        except Exception as e:
            print(f"❌ Error tracking output: {e}")

    def track_metrics(self, **kwargs):
        """
        Track success metrics for the execution
        
        Args:
            **kwargs: Metric names and values
                - test_coverage: Percentage (0-100)
                - code_quality_score: Score (0-10)
                - performance_latency_ms: Milliseconds
                - lines_of_code: Count
                
        Example:
            learning.track_metrics(
                test_coverage=92,
                code_quality_score=8.7,
                lines_of_code=750,
                performance_latency_ms=35
            )
        """
        if not self.agent_support:
            return
        
        try:
            self.agent_support.track_execution_metrics(**kwargs)
        except Exception as e:
            print(f"❌ Error tracking metrics: {e}")

    def post_execute(
        self,
        agent_id: str,
        status: str = "completed",
        result: Optional[Dict] = None
    ) -> Dict:
        """
        Post-execution hook: End execution and trigger autonomous learning
        
        This automatically:
        1. Records the execution
        2. Analyzes patterns with ReflectionAgent
        3. Updates the agent spec if learnings exist
        4. Versions previous spec
        5. Broadcasts updates to delegation system
        
        Call this after agent task execution completes.
        
        Args:
            agent_id: ID of agent that executed
            status: Execution status (completed, failed, partial)
            result: Optional result object
            
        Returns:
            Learning cycle result dict with:
                - success: bool
                - agent_id: str
                - spec_version: int
                - learnings: dict
                - changes: str
                - governance_note: Optional[str]
                
        Example:
            result = learning.post_execute(
                "backend_engineer",
                status="completed",
                result={"files_created": ["api.py", "models.py"]}
            )
            if result["success"]:
                print(f"Spec updated to v{result['spec_version']}")
        """
        if not self.agent_support:
            return {
                "success": False,
                "message": "Learning system unavailable"
            }
        
        try:
            return self.agent_support.end_execution_and_learn(
                agent_id, 
                status=status, 
                result=result
            )
        except Exception as e:
            print(f"❌ Error in post_execute: {e}")
            return {
                "success": False,
                "message": str(e)
            }

    def get_agent_stats(self, agent_id: str) -> Dict:
        """
        Get execution and learning statistics for an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Statistics dict with execution counts, tools used, etc.
        """
        if not self.agent_support:
            return {}
        
        try:
            return self.agent_support.get_agent_stats(agent_id)
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}

    def get_agent_evolution(self, agent_id: str) -> Dict:
        """
        Get evolution summary for an agent across versions
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Evolution data with version history and growth metrics
        """
        if not self.agent_support:
            return {}
        
        try:
            return self.agent_support.get_agent_evolution(agent_id)
        except Exception as e:
            print(f"❌ Error getting evolution: {e}")
            return {}

    def get_spec_history(self, agent_id: str) -> list:
        """Get version history for agent spec"""
        if not self.agent_support:
            return []
        
        try:
            return self.agent_support.get_spec_history(agent_id)
        except Exception as e:
            print(f"❌ Error getting history: {e}")
            return []

    def rollback_spec(self, agent_id: str, target_version: int) -> bool:
        """
        Rollback agent spec to a previous version
        
        Args:
            agent_id: Agent ID
            target_version: Version number to rollback to
            
        Returns:
            True if successful
        """
        if not self.agent_support:
            return False
        
        try:
            return self.agent_support.rollback_spec(agent_id, target_version)
        except Exception as e:
            print(f"❌ Error rolling back: {e}")
            return False


def execute_with_learning(
    company_dir: str,
    agent_id: str,
    task_description: str,
    task_func,
    *args,
    **kwargs
) -> tuple:
    """
    Convenience function to execute a task with automatic learning tracking
    
    This wraps a task function with pre/post execution hooks.
    
    Args:
        company_dir: Path to company directory
        agent_id: Agent executing the task
        task_description: Task description
        task_func: Function to execute
        *args: Arguments to pass to task_func
        **kwargs: Keyword arguments to pass to task_func
        
    Returns:
        (task_result, learning_result) tuple
        
    Example:
        def my_task(param1, param2):
            # Do work here
            return "result"
        
        result, learning = execute_with_learning(
            "./company",
            "backend_engineer",
            "Design API",
            my_task,
            param1="value1",
            param2="value2"
        )
    """
    learning = LearningIntegration(company_dir)
    
    # Pre-execution
    learning.pre_execute(agent_id, task_description)
    
    # Execute task
    try:
        task_result = task_func(*args, **kwargs)
        status = "completed"
    except Exception as e:
        task_result = None
        status = "failed"
        print(f"❌ Task execution failed: {e}")
    
    # Post-execution
    learning_result = learning.post_execute(
        agent_id,
        status=status,
        result={"task": task_description, "status": status}
    )
    
    return task_result, learning_result


if __name__ == "__main__":
    # Demo usage
    learning = LearningIntegration(".")
    
    if learning.is_available():
        print("✓ Learning integration available")
        
        # Simulate execution
        exec_id = learning.pre_execute("backend_engineer", "Design REST API")
        learning.track_tool("FastAPI", "API framework")
        learning.track_tool("PostgreSQL", "Database")
        learning.track_decision("Use async/await", "Better performance")
        learning.track_metrics(test_coverage=90, code_quality_score=8.5)
        result = learning.post_execute("backend_engineer")
        print(f"\nLearning result: {result}")
    else:
        print("⚠ Learning integration not available")
