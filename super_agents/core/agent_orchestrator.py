#!/usr/bin/env python3
"""
AICODE Labs - Agent Orchestrator v2.0

This script demonstrates how to instantiate and coordinate the AI agents
defined in the YAML configuration files. Version 2.0 includes cognitive
reasoning, governance, and expanded agent roster.

Integrated with autonomous spec regeneration system for continuous learning.
"""

import os
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml

# Import agent support for autonomous learning
try:
    from agent_support import AgentSupport

    HAS_AGENT_SUPPORT = True
except ImportError:
    HAS_AGENT_SUPPORT = False
    AgentSupport = None


@dataclass
class AgentSpec:
    """Represents an agent specification from YAML"""

    id: str
    title: str
    mission: str
    capabilities: List[str]
    personality: Dict[str, Any]
    runtime_config: Dict[str, Any]
    inputs: List[str] = None
    outputs: List[str] = None
    tools: List[str] = None
    delegates_to: List[str] = None
    controls: List[str] = None


class CognitiveReasoning:
    """Implements cognitive reasoning capabilities for agents"""

    @staticmethod
    def daily_reflection(
        agent_id: str, activities: List[str], outcomes: List[str]
    ) -> Dict[str, Any]:
        """Perform daily reflection on agent activities and outcomes"""
        print(
            f"  [{agent_id}] Reflecting on {len(activities)} activities and {len(outcomes)} outcomes"
        )

        # Simulate reflection process
        improvements = []
        for activity in activities:
            if random.choice([True, False]):  # Random improvement identification
                improvements.append(f"Improve {activity} by optimizing approach")

        return {
            "reflections": f"Reviewed {len(activities)} activities",
            "improvements_identified": improvements,
            "performance_score": random.uniform(0.7, 1.0),
        }

    @staticmethod
    def apply_decision_weighting(agent_role: str, decision_context: str) -> float:
        """Apply decision weighting based on agent role priority"""
        weights = {
            "executive": 1.0,  # CEO, CTO, COO
            "engineering": 0.9,  # Engineering roles
            "product": 0.8,  # Product roles
            "governance": 0.7,  # Governance roles
        }

        # Map agent to appropriate weight
        role_category = "governance"  # Default
        if any(role in agent_role.lower() for role in ["ceo", "cto", "coo"]):
            role_category = "executive"
        elif any(role in agent_role.lower() for role in ["engineer", "ai", "devops"]):
            role_category = "engineering"
        elif any(role in agent_role.lower() for role in ["product", "ux", "market"]):
            role_category = "product"

        return weights.get(role_category, 0.7)

    @staticmethod
    def majority_voting(
        options: List[Dict[str, Any]], agent_votes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Resolve conflicts through majority voting"""
        print(
            f"  Resolving conflict with {len(agent_votes)} votes on {len(options)} options"
        )

        # Count votes for each option
        vote_counts = dict.fromkeys(range(len(options)), 0)
        for vote in agent_votes:
            option_idx = vote.get("option", 0)
            if option_idx < len(options):
                vote_counts[option_idx] += 1

        # Find the most voted option
        winner_idx = max(vote_counts, key=vote_counts.get)
        winner = options[winner_idx]
        print(f"  Selected option {winner_idx} as the majority choice")

        return winner


class Agent:
    """Base class for all AI agents with cognitive reasoning and autonomous learning"""

    def __init__(self, spec: AgentSpec, agent_support: Optional["AgentSupport"] = None):
        self.spec = spec
        self.id = spec.id
        self.name = spec.title
        self.mission = spec.mission
        self.capabilities = spec.capabilities
        self.personality = spec.personality
        self.runtime_config = spec.runtime_config
        self.status = "initialized"
        self.last_activity = None
        self.activity_log = []
        self.agent_support = agent_support  # For autonomous learning
        self.tools_used_in_task = []
        self.decisions_made_in_task = []
        self.blockers_in_task = []
        self.outputs_created_in_task = []

    def execute_task(self, task_description: str, context: Dict[str, Any] = None):
        """Execute a task based on the agent's capabilities with cognitive reasoning and learning"""
        self.status = "working"
        self.last_activity = datetime.now()
        print(f"[{self.id}] {self.name} is working on: {task_description}")

        # 1. PRE-EXECUTION HOOK: Start tracking execution
        if self.agent_support:
            self.agent_support.track_execution_start(self.id, task_description)

        # Log the activity
        self.activity_log.append(
            {"task": task_description, "start_time": datetime.now(), "context": context}
        )

        # Reset tracking for this task
        self.tools_used_in_task = []
        self.decisions_made_in_task = []
        self.blockers_in_task = []
        self.outputs_created_in_task = []

        # Simulate work based on capabilities
        for capability in self.capabilities:
            print(f"  - Using capability: {capability}")
            # Track the capability as a tool/decision
            if self.agent_support:
                self.agent_support.track_execution_tool(
                    capability, f"Applied in task: {task_description}"
                )
                self.tools_used_in_task.append(capability)
            time.sleep(0.3)  # Simulate work

        # Apply cognitive reasoning
        self.apply_cognitive_reasoning(task_description)

        # Track a generic decision
        decision = f"Executed task using {len(self.capabilities)} capabilities"
        self.decisions_made_in_task.append(decision)
        if self.agent_support:
            self.agent_support.track_execution_decision(
                decision, "Task completed successfully"
            )

        # Track metrics
        if self.agent_support:
            self.agent_support.track_execution_metrics(
                test_coverage=85,
                code_quality_score=8.5,
                lines_of_code=450,
                performance_latency_ms=150,
            )

        self.status = "completed"
        self.activity_log[-1]["end_time"] = datetime.now()
        print(f"[{self.id}] {self.name} completed: {task_description}")

        # 2. POST-EXECUTION HOOK: End execution and trigger learning cycle
        if self.agent_support:
            result = {
                "task": task_description,
                "status": "completed",
                "capabilities_used": self.capabilities,
                "tools_used": self.tools_used_in_task,
                "decisions": self.decisions_made_in_task,
            }
            self.agent_support.end_execution_and_learn(
                self.id, status="completed", result=result
            )

        return f"Task completed by {self.name}"

    def apply_cognitive_reasoning(self, task_description: str):
        """Apply cognitive reasoning to the task"""
        # Reflection: analyze what was done and how it could be improved
        if random.choice([True, False]):  # Sometimes perform reflection
            reflection = CognitiveReasoning.daily_reflection(
                self.id, [task_description], ["completed successfully"]
            )
            print(f"  [{self.id}] Reflection: {reflection['reflections']}")

    def get_status(self):
        """Get current status of the agent"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "last_activity": self.last_activity,
            "capabilities": self.capabilities,
            "activity_count": len(self.activity_log),
        }


class AgentOrchestrator:
    """Orchestrates the AI agents based on the company structure with cognitive reasoning and autonomous learning"""

    def __init__(self, agents_dir: str):
        self.agents_dir = agents_dir
        self.agents = {}
        self.agent_specs = {}
        self.communication_graph = {}
        self.cognitive_reasoning = CognitiveReasoning()

        # Initialize agent support for autonomous learning
        self.agent_support = None
        if HAS_AGENT_SUPPORT:
            try:
                self.agent_support = AgentSupport(agents_dir)
                print("✓ Autonomous spec regeneration system initialized")
            except Exception as e:
                print(f"⚠ Could not initialize autonomous learning: {e}")

    def load_agent_specs(self):
        """Load all agent specifications from YAML files"""
        agents_dir = self.agents_dir

        for filename in os.listdir(agents_dir):
            if filename.endswith("_agent.yaml"):
                filepath = os.path.join(agents_dir, filename)
                with open(filepath, "r") as f:
                    spec_data = yaml.safe_load(f)

                spec = AgentSpec(
                    id=spec_data.get("id"),
                    title=spec_data.get("title"),
                    mission=spec_data.get("mission", ""),
                    capabilities=spec_data.get("capabilities", []),
                    personality=spec_data.get("personality", {}),
                    runtime_config=spec_data.get("runtime_config", {}),
                    inputs=spec_data.get("inputs", []),
                    outputs=spec_data.get("outputs", []),
                    tools=spec_data.get("tools", []),
                    delegates_to=spec_data.get("delegates_to", []),
                    controls=spec_data.get("controls", []),
                )

                self.agent_specs[spec.id] = spec
                print(f"Loaded agent spec: {spec.id} - {spec.title}")

    def instantiate_agents(self):
        """Create agent instances from specifications with learning support"""
        for agent_id, spec in self.agent_specs.items():
            agent = Agent(spec, agent_support=self.agent_support)
            self.agents[agent_id] = agent
            print(f"Instantiated agent: {agent_id}")

    def establish_communication_graph(self):
        """Establish communication relationships between agents based on delegates_to"""
        for agent_id, spec in self.agent_specs.items():
            if spec.delegates_to:
                self.communication_graph[agent_id] = spec.delegates_to
                print(f"{agent_id} delegates to: {spec.delegates_to}")

    def start_agents(self, startup_order: List[str]):
        """Start agents in the specified order"""
        print("\nStarting agents in order...")
        for agent_id in startup_order:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                print(f"Started {agent.name} (ID: {agent_id})")
                # Simulate startup process
                time.sleep(0.2)

    def _run_executive_phase(self):
        """Execute the strategic planning phase."""
        print("\n1. EXECUTIVE PHASE: Strategic Planning & Resource Allocation")
        ceo = self.agents.get("ceo")
        if ceo:
            ceo.execute_task(
                "Define quarterly strategic objectives and allocate resources", {}
            )

        cto = self.agents.get("cto")
        if cto:
            cto.execute_task("Architect AI systems and define technical standards", {})

        coo = self.agents.get("coo")
        if coo:
            coo.execute_task("Plan operational workflows and resource distribution", {})

    def _run_product_phase(self):
        """Execute the market research and product definition phase."""
        print("\n2. PRODUCT PHASE: Market Research & Specification")
        market_analyst = self.agents.get("market_analyst")
        if market_analyst:
            market_analyst.execute_task("Analyze market trends and user insights", {})

        product_manager = self.agents.get("product_manager")
        if product_manager:
            product_manager.execute_task("Create detailed product specifications", {})

        ux_designer = self.agents.get("ux_designer")
        if ux_designer:
            ux_designer.execute_task("Design user interface flows and experiences", {})

    def _run_engineering_phase(self):
        """Execute the technical implementation phase."""
        print("\n3. ENGINEERING PHASE: Technical Implementation")
        ai_engineer = self.agents.get("ai_engineer")
        if ai_engineer:
            ai_engineer.execute_task(
                "Design and implement AI models and reasoning chains", {}
            )

        backend_engineer = self.agents.get("backend_engineer")
        if backend_engineer:
            backend_engineer.execute_task(
                "Build backend API services and database layers", {}
            )

        frontend_engineer = self.agents.get("frontend_engineer")
        if frontend_engineer:
            frontend_engineer.execute_task(
                "Implement frontend UI components and state management", {}
            )

        devops_engineer = self.agents.get("devops_engineer")
        if devops_engineer:
            devops_engineer.execute_task(
                "Create CI/CD pipeline and deployment infrastructure", {}
            )

        builder_engineer = self.agents.get("builder_engineer")
        if builder_engineer:
            builder_engineer.execute_task(
                "Convert specifications to runnable codebase", {}
            )

    def _run_quality_phase(self):
        """Execute the quality assurance and security phase."""
        print("\n4. QUALITY & SECURITY PHASE: Validation & Protection")
        security_engineer = self.agents.get("security_engineer")
        if security_engineer:
            security_engineer.execute_task(
                "Implement authentication and security measures", {}
            )

        qa_engineer = self.agents.get("qa_engineer")
        if qa_engineer:
            qa_engineer.execute_task(
                "Run comprehensive integration and performance tests", {}
            )

        reliability_engineer = self.agents.get("reliability_engineer")
        if reliability_engineer:
            reliability_engineer.execute_task(
                "Monitor system health and ensure uptime", {}
            )

    def _run_operations_phase(self):
        """Execute the operations and knowledge management phase."""
        print("\n5. OPERATIONS & KNOWLEDGE PHASE: Management & Documentation")
        tech_writer = self.agents.get("tech_writer")
        if tech_writer:
            tech_writer.execute_task("Generate API documentation and user guides", {})

        knowledge_architect = self.agents.get("knowledge_architect")
        if knowledge_architect:
            knowledge_architect.execute_task(
                "Update knowledge graph and vector memory", {}
            )

        ops_automator = self.agents.get("ops_automator")
        if ops_automator:
            ops_automator.execute_task("Automate maintenance and reporting tasks", {})

    def _run_expansion_phase(self):
        """Execute the expansion and research phase."""
        print("\n6. EXPANSION PHASE: Advanced Capabilities")
        finance_agent = self.agents.get("finance_agent")
        if finance_agent:
            finance_agent.execute_task("Model costs and allocate API key budgets", {})

        partnership_agent = self.agents.get("partnership_agent")
        if partnership_agent:
            partnership_agent.execute_task(
                "Explore external integrations and partnerships", {}
            )

        prompt_engineer = self.agents.get("prompt_engineer")
        if prompt_engineer:
            prompt_engineer.execute_task("Optimize prompts for all AI agents", {})

        research_agent = self.agents.get("research_agent")
        if research_agent:
            research_agent.execute_task("Research new models and techniques", {})

    def _run_governance_phase(self):
        """Execute the governance and release phase."""
        print("\n7. GOVERNANCE PHASE: Review & Release")
        meta_architect = self.agents.get("meta_architect")
        if meta_architect:
            meta_architect.execute_task(
                "Validate compliance and evolve agent specs", {}
            )

        coo = self.agents.get("coo")
        if coo:
            coo.execute_task("Coordinate final release process", {})

        ceo = self.agents.get("ceo")
        if ceo:
            ceo.execute_task("Provide final approval for production release", {})

    def run_demo_workflow(self):
        """Demonstrate a comprehensive workflow between agents with cognitive reasoning"""
        print("\n" + "=" * 60)
        print("DEMONSTRATING AI COMPANY WORKFLOW v2.0")
        print("With Cognitive Reasoning and Expanded Agent Roster")
        print("=" * 60)

        # Execute all phases in sequence
        self._run_executive_phase()
        self._run_product_phase()
        self._run_engineering_phase()
        self._run_quality_phase()
        self._run_operations_phase()
        self._run_expansion_phase()
        self._run_governance_phase()

        print("\nCOMPREHENSIVE WORKFLOW DEMONSTRATED SUCCESSFULLY!")

    def get_all_statuses(self):
        """Get status of all agents"""
        return {agent_id: agent.get_status() for agent_id, agent in self.agents.items()}


def main():
    """Main function to run the AI company orchestrator v2.0"""
    print("Initializing AICODE Labs v2.0 - AI-Native Software Development Company")
    print("Loading agent specifications and preparing for execution...\n")

    # Initialize orchestrator
    agents_dir = os.path.join(os.path.dirname(__file__), "..", "agents")
    agents_dir = os.path.abspath(agents_dir)
    orchestrator = AgentOrchestrator(agents_dir)

    # Load and instantiate agents
    orchestrator.load_agent_specs()
    orchestrator.instantiate_agents()
    orchestrator.establish_communication_graph()

    # Get startup order from runtime config
    runtime_config_path = os.path.join(agents_dir, "..", "runtime_config.yaml")
    with open(runtime_config_path, "r") as f:
        runtime_data = yaml.safe_load(f)

    startup_order = runtime_data.get("lifecycle", {}).get("startup_order", [])
    orchestrator.start_agents(startup_order)

    # Run a comprehensive demonstration workflow
    orchestrator.run_demo_workflow()

    # Show final statuses
    print("\n" + "=" * 60)
    print("FINAL AGENT STATUSES")
    print("=" * 60)
    statuses = orchestrator.get_all_statuses()
    for agent_id, status in statuses.items():
        print(
            f"{agent_id}: {status['status']} (Tasks: {status['activity_count']}, Last activity: {status['last_activity']})"
        )

    # Summary
    active_agents = len([s for s in statuses.values() if s["activity_count"] > 0])
    print(
        f"\nSUMMARY: {active_agents} of {len(statuses)} agents were active in this workflow"
    )


if __name__ == "__main__":
    main()
