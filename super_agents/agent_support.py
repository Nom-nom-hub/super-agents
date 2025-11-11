#!/usr/bin/env python3
"""
AICODE Labs - Agent Support Module

Provides multi-agent support for external AI agents (Claude, Copilot, Amp, etc.)
Inspired by GitHub Spec Kit's agent-agnostic design pattern.
"""

import os
import shutil
import sys
from typing import Dict, List, Optional

import yaml

# Import the structured logging module
try:
    from .utils.structured_logging import get_logger
except ImportError:
    # For development/standalone execution
    super_agents_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(super_agents_dir, "utils"))
    from structured_logging import get_logger

# Import the delegation prompt generator for intelligent routing
try:
    from .core.delegation_prompt_generator import DelegationPromptGenerator

    HAS_DELEGATION_GENERATOR = True
except ImportError:
    HAS_DELEGATION_GENERATOR = False
    DelegationPromptGenerator = None

# Import autonomous spec regeneration components
try:
    from .core.autonomous_spec_manager import AutonomousSpecManager, SpecValidator
    from .core.execution_tracker import ExecutionTracker
    from .core.reflection_agent import ReflectionAgent

    HAS_SPEC_REGENERATION = True
except ImportError:
    HAS_SPEC_REGENERATION = False
    ExecutionTracker = None
    ReflectionAgent = None
    AutonomousSpecManager = None
    SpecValidator = None


class AgentSupport:
    """Handles multi-agent integration and command generation"""

    def __init__(self, agents_dir: str = "."):
        """
        Initialize agent support system

        Args:
            agents_dir: Path to the root directory that contains the agents subdirectory
        """
        self.agents_dir = os.path.join(agents_dir, "agents")
        self.registry_path = os.path.join(agents_dir, "agent_registry.yaml")
        self.templates_dir = os.path.join(agents_dir, "templates")
        self.registry = self._load_registry()

        # Initialize structured logging
        self.logger = get_logger(
            self.__class__.__name__, log_dir=os.path.join(agents_dir, "logs")
        )

        # Initialize delegation prompt generator if available
        self.delegation_generator = None
        if HAS_DELEGATION_GENERATOR:
            try:
                self.delegation_generator = DelegationPromptGenerator(agents_dir)
            except Exception as e:
                print(f"⚠ Could not initialize delegation generator: {e}")

        # Initialize autonomous spec regeneration components if available
        self.execution_tracker = None
        self.reflection_agent = None
        self.spec_manager = None

        if HAS_SPEC_REGENERATION:
            try:
                self.execution_tracker = ExecutionTracker(agents_dir)
                self.reflection_agent = ReflectionAgent(agents_dir)
                self.spec_manager = AutonomousSpecManager(agents_dir)
            except Exception as e:
                print(f"⚠ Could not initialize spec regeneration: {e}")

    def _load_registry(self) -> Dict:
        """Load agent registry from YAML"""
        if not os.path.exists(self.registry_path):
            # Try to copy the default registry from the package if it doesn't exist
            self._ensure_default_registry()

        if not os.path.exists(self.registry_path):
            # If still not found, return an empty registry
            # This allows the class to function even without a registry file
            return {"agents": {}}

        with open(self.registry_path, "r") as f:
            data = yaml.safe_load(f)

        return data or {"agents": {}}

    def _ensure_default_registry(self) -> None:
        """Copy the default agent registry file from the package if it doesn't exist"""
        import os
        import shutil

        # Get the path to the package's registry file based on this file's location
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        package_registry_path = os.path.join(current_file_dir, "agent_registry.yaml")

        # Check if the package registry file exists
        if os.path.exists(package_registry_path):
            # Copy the file to the target directory
            shutil.copy2(package_registry_path, self.registry_path)
        else:
            # Fallback: create a minimal registry if we can't find the package version
            default_registry = {
                "agents": {
                    "claude": {
                        "name": "Claude Code",
                        "folder": ".claude/commands/",
                        "format": "markdown",
                        "cli_tool": "claude",
                        "requires_cli": True,
                        "placeholder": "$ARGUMENTS",
                        "file_extension": "md",
                        "description": "Anthropic's Claude Code CLI for AI-assisted development",
                    },
                    "copilot": {
                        "name": "GitHub Copilot",
                        "folder": ".github/prompts/",
                        "format": "markdown",
                        "cli_tool": None,
                        "requires_cli": False,
                        "placeholder": "$ARGUMENTS",
                        "file_extension": "md",
                        "description": "GitHub Copilot integrated into VS Code",
                    },
                    "amp": {
                        "name": "Amp",
                        "folder": ".agents/commands/",
                        "format": "markdown",
                        "cli_tool": "amp",
                        "requires_cli": True,
                        "placeholder": "$ARGUMENTS",
                        "file_extension": "md",
                        "description": "Sourcegraph's Amp AI coding agent",
                    },
                    "cursor": {
                        "name": "Cursor",
                        "folder": ".cursor/commands/",
                        "format": "markdown",
                        "cli_tool": "cursor-agent",
                        "requires_cli": True,
                        "placeholder": "$ARGUMENTS",
                        "file_extension": "md",
                        "description": "Cursor IDE with agent capabilities",
                    },
                },
                "default_commands": [
                    {
                        "name": "super-agents-init",
                        "description": "Initialize connection to AICODE Labs super-agents system",
                    },
                    {
                        "name": "list-agents",
                        "description": "List all available super-agents and their capabilities",
                    },
                    {
                        "name": "agent-help",
                        "description": "Get detailed information about a specific super-agent",
                    },
                    {
                        "name": "delegate-task",
                        "description": "Delegate a task to a super-agent",
                    },
                ],
            }

            # Write the default registry to the target file
            with open(self.registry_path, "w") as f:
                yaml.dump(
                    default_registry, f, default_flow_style=False, sort_keys=False
                )

    def get_agent_config(self, agent_id: str) -> Optional[Dict]:
        """Get configuration for a specific agent"""
        return self.registry.get("agents", {}).get(agent_id)

    def list_registered_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self.registry.get("agents", {}).keys())

    def detect_available_agents(self) -> Dict[str, bool]:
        """
        Check which agents are available on the system

        Returns:
            Dict mapping agent_id to availability (True/False)
        """
        available = {}
        agents = self.registry.get("agents", {})

        for agent_id, config in agents.items():
            if not config.get("requires_cli"):
                available[agent_id] = True
            else:
                cli_tool = config.get("cli_tool")
                available[agent_id] = shutil.which(cli_tool) is not None

        return available

    def get_available_agents(self) -> List[str]:
        """Get list of available agents only"""
        available = self.detect_available_agents()
        return [
            agent_id for agent_id, is_available in available.items() if is_available
        ]

    def load_agent_specs(self) -> Dict[str, Dict]:
        """Load all super-agent specifications from YAML files"""
        specs = {}

        # Ensure agents directory exists
        os.makedirs(self.agents_dir, exist_ok=True)

        # Check if the agents directory is empty
        if not os.listdir(self.agents_dir):
            # Copy default agent spec files from the package
            self._ensure_default_agent_specs()

        # Now load all agent spec files
        for filename in os.listdir(self.agents_dir):
            if filename.endswith("_agent.yaml"):
                filepath = os.path.join(self.agents_dir, filename)
                with open(filepath, "r") as f:
                    spec_data = yaml.safe_load(f)
                    agent_id = spec_data.get("id")
                    if agent_id:  # Only add if there's an id
                        specs[agent_id] = spec_data

        return specs

    def _find_package_agents_dir(self) -> Optional[str]:
        """Try multiple methods to locate the package's agents directory"""
        # Method 1: Using __file__ attribute
        if hasattr(self, "__file__") or "__file__" in globals():
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            potential_dir = os.path.join(os.path.dirname(current_file_dir), "agents")
            if os.path.exists(potential_dir):
                return potential_dir

        # Method 2: Try to import super_agents module to find the path
        try:
            import super_agents

            super_agents_dir = os.path.dirname(super_agents.__file__)
            potential_dir = os.path.join(super_agents_dir, "agents")
            if os.path.exists(potential_dir):
                return potential_dir
        except ImportError:
            pass

        # Method 3: If current file is inside the package, try relative paths
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_file_dir)
        potential_dir = os.path.join(parent_dir, "agents")
        if os.path.exists(potential_dir):
            return potential_dir

        return None

    def _copy_agent_specs_from_package(self, package_agents_dir: str) -> int:
        """Copy all agent spec files from package directory"""
        agent_files_copied = 0
        for filename in os.listdir(package_agents_dir):
            if filename.endswith("_agent.yaml"):
                source_path = os.path.join(package_agents_dir, filename)
                dest_path = os.path.join(self.agents_dir, filename)
                shutil.copy2(source_path, dest_path)
                agent_files_copied += 1
        return agent_files_copied

    def _ensure_default_agent_specs(self) -> None:
        """Copy default agent spec files from the package if agents directory is empty"""
        package_agents_dir = self._find_package_agents_dir()

        if package_agents_dir:
            agent_files_copied = self._copy_agent_specs_from_package(package_agents_dir)
            if agent_files_copied == 0 and not os.listdir(self.agents_dir):
                self._create_fallback_agent_specs()
        else:
            self._create_fallback_agent_specs()

    def _create_fallback_agent_specs(self) -> None:
        """Create a comprehensive set of default agent specs as a fallback"""

        # Define comprehensive agent specs for all 22 agents
        comprehensive_agent_specs = {
            "ceo": {
                "id": "ceo",
                "title": "Chief Executive Officer Agent",
                "mission": "Direct company vision, resource allocation, and long-term roadmap. Make strategic decisions and ensure alignment with business objectives.",
                "division": "Executive",
                "delegates_to": ["cto", "coo", "product_manager"],
                "controls": [
                    "company_strategy.md",
                    "quarterly_objectives.yaml",
                    "resource_allocation_plan.yaml",
                ],
                "inputs": [
                    "market_reports.yaml",
                    "financial_summaries.csv",
                    "team_performance_data.json",
                ],
                "outputs": [
                    "strategic_directives.md",
                    "company_vision_doc.md",
                    "resource_allocation_plan.yaml",
                ],
                "tools": [
                    "strategy_vision_sdk",
                    "resource_allocator",
                    "stakeholder_manager",
                ],
                "capabilities": [
                    "strategic_decision_making",
                    "resource_allocation",
                    "vision_setting",
                    "stakeholder_communication",
                    "risk_assessment",
                    "compliance_monitoring",
                    "long_term_planning",
                    "market_positioning",
                    "company_alignment",
                ],
                "permissions": ["highest", "admin_access", "budget_approval"],
                "decision_making_authority": {
                    "product_strategy": "final",
                    "resource_allocation": "final",
                    "market_direction": "final",
                    "team_structure": "final",
                },
                "personality": {
                    "visionary": True,
                    "decisive": True,
                    "stakeholder_focused": True,
                    "strategic_thinking": True,
                    "big_picture_oriented": True,
                },
                "workflows": [
                    "strategic_planning_cycle",
                    "quarterly_review_process",
                    "resource_allocation_workflow",
                    "stakeholder_communication_protocol",
                ],
                "success_metrics": [
                    "company_growth_rate",
                    "market_share",
                    "employee_satisfaction",
                    "customer_acquisition_cost",
                    "revenue_per_employee",
                ],
                "runtime_config": {
                    "priority": "highest",
                    "access_level": "admin",
                    "review_required": False,
                    "escalation_threshold": "strategic_impact",
                },
            },
            "cto": {
                "id": "cto",
                "title": "Chief Technology Officer Agent",
                "mission": "Architect the AI ecosystem, define technology standards, ensure system scalability, and maintain technical excellence across all products and services.",
                "division": "Executive",
                "delegates_to": [
                    "backend_engineer",
                    "frontend_engineer",
                    "ai_engineer",
                    "devops_engineer",
                ],
                "controls": [
                    "technical_architecture_doc.md",
                    "technology_roadmap.yaml",
                    "security_standards.md",
                ],
                "inputs": [
                    "product_requirements.yaml",
                    "performance_benchmarks.csv",
                    "security_audits.json",
                ],
                "outputs": [
                    "system_architecture_doc.md",
                    "technology_decisions_log.md",
                    "security_compliance_report.md",
                ],
                "tools": [
                    "architecture_designer",
                    "tech_stack_analyzer",
                    "security_compliance_checker",
                    "performance_profiler",
                ],
                "capabilities": [
                    "system_architecture",
                    "technology_standards",
                    "scalability_planning",
                    "technical_vision",
                    "infrastructure_design",
                    "security_implementation",
                    "performance_optimization",
                    "technical_debt_management",
                    "platform_engineering",
                ],
                "permissions": [
                    "admin_access",
                    "system_config",
                    "security_policy",
                    "infrastructure_control",
                ],
                "decision_making_authority": {
                    "technology_choices": "final",
                    "architecture_decisions": "final",
                    "security_standards": "final",
                    "technical_standards": "final",
                },
                "personality": {
                    "innovative": True,
                    "technical": True,
                    "architecture_focused": True,
                    "forward_thinking": True,
                    "quality_oriented": True,
                },
                "workflows": [
                    "architecture_review_process",
                    "technology_evaluation_workflow",
                    "security_compliance_check",
                    "technical_debt_management_cycle",
                ],
                "success_metrics": [
                    "system_scalability",
                    "technical_debt_ratio",
                    "security_compliance_score",
                    "performance_benchmarks",
                    "developer_productivity_index",
                ],
                "runtime_config": {
                    "priority": "high",
                    "access_level": "admin",
                    "review_required": True,
                    "escalation_threshold": "system_impact",
                },
            },
            "coo": {
                "id": "coo",
                "title": "Chief Operations Officer Agent",
                "mission": "Oversee day-to-day operations, optimize processes, ensure efficiency, and maintain operational excellence across all company functions.",
                "division": "Executive",
                "delegates_to": [
                    "ops_automator",
                    "reliability_engineer",
                    "devops_engineer",
                ],
                "controls": [
                    "operational_procedures_manual.md",
                    "efficiency_metrics_dashboard.yaml",
                    "process_documentation.csv",
                ],
                "inputs": [
                    "operational_logs.json",
                    "efficiency_metrics.csv",
                    "resource_utilization_data.yaml",
                ],
                "outputs": [
                    "operational_optimization_plan.md",
                    "process_improvement_documentation.md",
                    "efficiency_reporting.yaml",
                ],
                "tools": [
                    "process_optimizer",
                    "resource_scheduler",
                    "efficiency_analyzer",
                    "operations_dashboard",
                ],
                "capabilities": [
                    "process_optimization",
                    "resource_allocation",
                    "efficiency_monitoring",
                    "operations_coordination",
                    "workflow_management",
                    "quality_assurance",
                    "cost_optimization",
                    "risk_management",
                    "performance_monitoring",
                ],
                "permissions": [
                    "operations_control",
                    "resource_allocation",
                    "process_management",
                ],
                "decision_making_authority": {
                    "operational_processes": "final",
                    "resource_allocation": "final",
                    "efficiency_improvements": "final",
                    "process_optimization": "final",
                },
                "personality": {
                    "efficient": True,
                    "systematic": True,
                    "process_oriented": True,
                    "detail_minded": True,
                    "optimization_focused": True,
                },
                "workflows": [
                    "daily_operations_workflow",
                    "process_improvement_cycle",
                    "resource_allocation_process",
                    "efficiency_monitoring_routine",
                ],
                "success_metrics": [
                    "operational_efficiency",
                    "resource_utilization_rate",
                    "process_automation_score",
                    "cost_per_operation",
                    "time_to_completion_metrics",
                ],
                "runtime_config": {
                    "priority": "high",
                    "access_level": "admin",
                    "review_required": True,
                    "escalation_threshold": "operational_risk",
                },
            },
            "product_manager": {
                "id": "product_manager",
                "title": "Product Manager Agent",
                "mission": "Define product vision, manage roadmap, prioritize features, and ensure products meet user needs and business objectives.",
                "division": "Product",
                "delegates_to": [
                    "ux_designer",
                    "backend_engineer",
                    "frontend_engineer",
                ],
                "controls": [
                    "product_roadmap.yaml",
                    "feature_requirements_spec.md",
                    "user_feedback_database.json",
                ],
                "inputs": [
                    "user_feedback.csv",
                    "market_research.json",
                    "usage_analytics.yaml",
                    "competitor_analysis.md",
                ],
                "outputs": [
                    "product_requirements_doc.md",
                    "feature_specifications.yaml",
                    "product_roadmap.yaml",
                    "success_metrics_report.md",
                ],
                "tools": [
                    "product_analytics_dashboard",
                    "user_feedback_analyzer",
                    "market_research_tool",
                    "feature_prioritization_framework",
                ],
                "capabilities": [
                    "product_strategy",
                    "feature_prioritization",
                    "user_research",
                    "market_analysis",
                    "product_roadmap_management",
                    "requirement_gathering",
                    "stakeholder_alignment",
                    "success_metrics_definition",
                    "product_lifecycle_management",
                ],
                "permissions": [
                    "feature_prioritization",
                    "product_decisions",
                    "user_research",
                    "stakeholder_communication",
                ],
                "decision_making_authority": {
                    "feature_priorities": "final",
                    "product_requirements": "final",
                    "user_experience_decisions": "final",
                    "product_vision": "final",
                },
                "personality": {
                    "user_focused": True,
                    "analytical": True,
                    "strategic": True,
                    "collaborative": True,
                    "data_driven": True,
                },
                "workflows": [
                    "feature_prioritization_process",
                    "user_research_workflow",
                    "product_roadmap_review",
                    "stakeholder_alignment_protocol",
                ],
                "success_metrics": [
                    "user_satisfaction_score",
                    "feature_adoption_rate",
                    "time_to_market",
                    "customer_retention_rate",
                    "product_usage_metrics",
                ],
                "runtime_config": {
                    "priority": "high",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "strategic_impact",
                },
            },
            "ux_designer": {
                "id": "ux_designer",
                "title": "UX/UI Designer Agent",
                "mission": "Design intuitive user experiences, create wireframes and prototypes, and ensure products meet accessibility and usability standards.",
                "division": "Product",
                "delegates_to": ["frontend_engineer", "product_manager"],
                "controls": [
                    "design_system.yaml",
                    "user_interface_guidelines.md",
                    "accessibility_standards.json",
                ],
                "inputs": [
                    "user_research.json",
                    "product_requirements.md",
                    "usability_test_results.csv",
                ],
                "outputs": [
                    "wireframes/",
                    "prototypes/",
                    "design_system.yaml",
                    "user_interface_spec.md",
                ],
                "tools": [
                    "design_toolkit",
                    "usability_analyzer",
                    "accessibility_checker",
                    "user_flow_designer",
                ],
                "capabilities": [
                    "user_experience_design",
                    "interface_design",
                    "user_research",
                    "usability_testing",
                    "accessibility_compliance",
                    "design_system_development",
                    "user_flow_optimization",
                    "interaction_design",
                    "visual_design",
                ],
                "permissions": [
                    "design_system",
                    "user_interface_spec",
                    "accessibility_standards",
                ],
                "decision_making_authority": {
                    "user_interface_design": "final",
                    "user_experience_decisions": "final",
                    "accessibility_compliance": "final",
                    "design_system_updates": "final",
                },
                "personality": {
                    "user_focused": True,
                    "creative": True,
                    "detail_oriented": True,
                    "empathetic": True,
                    "aesthetically_minded": True,
                },
                "workflows": [
                    "user_research_process",
                    "design_review_workflow",
                    "usability_testing_routine",
                    "design_system_maintenance",
                ],
                "success_metrics": [
                    "usability_score",
                    "accessibility_compliance",
                    "user_satisfaction",
                    "design_system_adoption",
                    "user_task_completion_rate",
                ],
                "runtime_config": {
                    "priority": "medium",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "user_experience_impact",
                },
            },
            "backend_engineer": {
                "id": "backend_engineer",
                "title": "Backend Engineer Agent",
                "mission": "Build core API services, database layers, business logic systems, and ensure scalable, secure server-side architecture.",
                "division": "Engineering",
                "delegates_to": ["devops_engineer", "qa_engineer", "security_engineer"],
                "controls": [
                    "api_specifications.yaml",
                    "database_schema.sql",
                    "server_architecture_docs.md",
                ],
                "inputs": [
                    "product_specifications.yaml",
                    "database_requirements.json",
                    "security_compliance_docs.md",
                ],
                "outputs": [
                    "api_service/",
                    "database_schema.sql",
                    "server_architecture_docs.md",
                    "api_documentation.md",
                ],
                "tools": [
                    "Python",
                    "FastAPI",
                    "PostgreSQL",
                    "Docker",
                    "Kubernetes",
                    "Testing_Frameworks",
                ],
                "capabilities": [
                    "api_development",
                    "database_design",
                    "business_logic_implementation",
                    "server_architecture",
                    "integration_development",
                    "performance_optimization",
                    "security_implementation",
                    "api_documentation",
                    "microservice_architecture",
                ],
                "permissions": [
                    "server_deployment",
                    "database_management",
                    "api_configuration",
                ],
                "decision_making_authority": {
                    "backend_architecture": "final",
                    "database_design": "final",
                    "api_design": "final",
                    "server_infrastructure": "implementation",
                },
                "personality": {
                    "logical": True,
                    "detail_oriented": True,
                    "problem_solver": True,
                    "systematic": True,
                    "performance_focused": True,
                },
                "workflows": [
                    "api_development_workflow",
                    "database_design_process",
                    "backend_testing_protocol",
                    "server_deployment_pipeline",
                ],
                "success_metrics": [
                    "api_response_time",
                    "system_scalability",
                    "code_quality_score",
                    "backend_test_coverage",
                    "database_performance",
                ],
                "runtime_config": {
                    "priority": "high",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "system_performance",
                },
            },
            "frontend_engineer": {
                "id": "frontend_engineer",
                "title": "Frontend Engineer Agent",
                "mission": "Build responsive user interfaces, implement UI components, optimize user experiences, and ensure cross-platform compatibility.",
                "division": "Engineering",
                "delegates_to": ["ux_designer", "qa_engineer"],
                "controls": [
                    "ui_component_library.yaml",
                    "frontend_architecture_doc.md",
                    "performance_metrics.json",
                ],
                "inputs": [
                    "ui_design_specs.yaml",
                    "api_endpoints.json",
                    "performance_requirements.md",
                ],
                "outputs": [
                    "ui_components/",
                    "frontend_architecture_doc.md",
                    "performance_metrics.json",
                    "user_interface_docs.md",
                ],
                "tools": [
                    "React",
                    "TypeScript",
                    "NextJS",
                    "CSS",
                    "Webpack",
                    "Testing_Libraries",
                ],
                "capabilities": [
                    "ui_component_development",
                    "responsive_design",
                    "user_interface_implementation",
                    "frontend_architecture",
                    "performance_optimization",
                    "cross_browser_compatibility",
                    "accessibility_implementation",
                    "state_management",
                    "frontend_testing",
                ],
                "permissions": [
                    "ui_component_library",
                    "frontend_deployment",
                    "user_interface_config",
                ],
                "decision_making_authority": {
                    "ui_component_architecture": "final",
                    "frontend_performance": "final",
                    "user_interface_implementation": "final",
                    "frontend_tooling": "implementation",
                },
                "personality": {
                    "user_focused": True,
                    "creative": True,
                    "detail_oriented": True,
                    "performance_minded": True,
                    "user_experience_conscious": True,
                },
                "workflows": [
                    "ui_component_development",
                    "frontend_performance_optimization",
                    "cross_browser_testing",
                    "user_interface_review_process",
                ],
                "success_metrics": [
                    "page_load_time",
                    "user_interface_performance",
                    "cross_browser_compatibility",
                    "frontend_test_coverage",
                    "user_engagement_metrics",
                ],
                "runtime_config": {
                    "priority": "high",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "user_experience_impact",
                },
            },
            "devops_engineer": {
                "id": "devops_engineer",
                "title": "DevOps Engineer Agent",
                "mission": "Manage CI/CD pipelines, infrastructure automation, deployment processes, and ensure system reliability and scalability.",
                "division": "Engineering",
                "delegates_to": ["reliability_engineer", "security_engineer"],
                "controls": [
                    "ci_cd_pipeline_config.yaml",
                    "infrastructure_templates.yaml",
                    "monitoring_dashboard.json",
                ],
                "inputs": [
                    "application_code/",
                    "deployment_configs.yaml",
                    "infrastructure_requirements.json",
                ],
                "outputs": [
                    "deployed_applications/",
                    "infrastructure_state.json",
                    "monitoring_dashboards/",
                    "deployment_logs/",
                ],
                "tools": [
                    "Docker",
                    "Kubernetes",
                    "Terraform",
                    "Jenkins",
                    "Prometheus",
                    "Grafana",
                ],
                "capabilities": [
                    "ci_cd_pipeline_management",
                    "infrastructure_as_code",
                    "deployment_automation",
                    "containerization",
                    "monitoring_implementation",
                    "infrastructure_scaling",
                    "security_integration",
                    "cloud_platform_management",
                    "performance_optimization",
                ],
                "permissions": [
                    "infrastructure_management",
                    "deployment_control",
                    "monitoring_access",
                    "cloud_platform_access",
                ],
                "decision_making_authority": {
                    "infrastructure_decisions": "final",
                    "deployment_processes": "final",
                    "ci_cd_configurations": "final",
                    "monitoring_policies": "final",
                },
                "personality": {
                    "systematic": True,
                    "reliability_focused": True,
                    "automation_oriented": True,
                    "efficiency_minded": True,
                    "process_driven": True,
                },
                "workflows": [
                    "ci_cd_pipeline_management",
                    "infrastructure_provisioning",
                    "deployment_automation_workflow",
                    "monitoring_and_alerting_setup",
                ],
                "success_metrics": [
                    "deployment_frequency",
                    "mean_time_to_recovery",
                    "infrastructure_cost_efficiency",
                    "system_availability",
                    "pipeline_success_rate",
                ],
                "runtime_config": {
                    "priority": "high",
                    "access_level": "admin",
                    "review_required": True,
                    "escalation_threshold": "infrastructure_risk",
                },
            },
            "qa_engineer": {
                "id": "qa_engineer",
                "title": "Quality Assurance Agent",
                "mission": "Validate system outputs, run integration tests, ensure production readiness, and maintain quality standards across all deliverables.",
                "division": "Quality",
                "delegates_to": ["backend_engineer", "frontend_engineer"],
                "controls": [
                    "test_automation_framework.yaml",
                    "quality_standards.md",
                    "test_case_library.json",
                ],
                "inputs": [
                    "build_artifacts/",
                    "feature_specifications.yaml",
                    "user_acceptance_criteria.md",
                ],
                "outputs": [
                    "qa_report.md",
                    "test_results.json",
                    "quality_metrics.yaml",
                    "bug_reports/",
                ],
                "tools": [
                    "pytest",
                    "Playwright",
                    "Selenium",
                    "Jira",
                    "Load_Testing_Tools",
                ],
                "capabilities": [
                    "test_automation",
                    "integration_testing",
                    "quality_assurance",
                    "bug_identification",
                    "performance_testing",
                    "regression_testing",
                    "user_acceptance_testing",
                    "quality_metrics_definition",
                    "test_case_management",
                ],
                "permissions": [
                    "testing_environment",
                    "bug_tracking_system",
                    "quality_metrics",
                ],
                "decision_making_authority": {
                    "quality_approval": "final",
                    "test_automation_framework": "final",
                    "quality_standards": "input",
                    "bug_severity_classification": "final",
                },
                "personality": {
                    "thorough": True,
                    "detail_oriented": True,
                    "quality_focused": True,
                    "methodical": True,
                    "accuracy_oriented": True,
                },
                "workflows": [
                    "test_automation_workflow",
                    "integration_testing_process",
                    "quality_gate_review",
                    "bug_triage_and_resolution",
                ],
                "success_metrics": [
                    "test_coverage_percentage",
                    "defect_detection_rate",
                    "quality_score",
                    "time_to_bug_resolution",
                    "regression_test_pass_rate",
                ],
                "runtime_config": {
                    "priority": "medium",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "quality_risk",
                },
            },
            "security_engineer": {
                "id": "security_engineer",
                "title": "Security Agent",
                "mission": "Implement security measures, conduct vulnerability assessments, ensure compliance, and protect systems from threats.",
                "division": "Quality",
                "delegates_to": ["backend_engineer", "devops_engineer", "qa_engineer"],
                "controls": [
                    "security_policy.yaml",
                    "vulnerability_database.json",
                    "compliance_framework.md",
                ],
                "inputs": [
                    "system_architecture.yaml",
                    "code_repository/",
                    "security_scan_results.json",
                ],
                "outputs": [
                    "security_report.md",
                    "vulnerability_assessment.yaml",
                    "compliance_certificate.json",
                    "security_monitoring_config.yaml",
                ],
                "tools": [
                    "OWASP_ZAP",
                    "SonarQube",
                    "Dependency_Checker",
                    "Vulnerability_Scanner",
                    "Penetration_Testing_Tools",
                ],
                "capabilities": [
                    "vulnerability_assessment",
                    "security_implementation",
                    "compliance_monitoring",
                    "threat_modeling",
                    "security_audit",
                    "penetration_testing",
                    "security_monitoring",
                    "incident_response",
                    "authentication_authorization",
                ],
                "permissions": [
                    "security_policy",
                    "vulnerability_scanning",
                    "compliance_checking",
                    "security_monitoring",
                ],
                "decision_making_authority": {
                    "security_implementations": "final",
                    "vulnerability_severity": "final",
                    "compliance_approvals": "final",
                    "security_controls": "final",
                },
                "personality": {
                    "security_focused": True,
                    "risk_aware": True,
                    "thorough": True,
                    "proactive": True,
                    "compliance_oriented": True,
                },
                "workflows": [
                    "vulnerability_assessment_process",
                    "security_implementation_workflow",
                    "compliance_checking_routine",
                    "incident_response_protocol",
                ],
                "success_metrics": [
                    "vulnerability_detection_rate",
                    "compliance_score",
                    "security_incident_response_time",
                    "zero_day_vulnerability_identification",
                    "security_test_coverage",
                ],
                "runtime_config": {
                    "priority": "high",
                    "access_level": "admin",
                    "review_required": True,
                    "escalation_threshold": "security_risk",
                },
            },
            "ai_engineer": {
                "id": "ai_engineer",
                "title": "AI Engineer Agent",
                "mission": "Design, develop, and optimize AI models, reasoning chains, and intelligent systems that enhance product capabilities.",
                "division": "Engineering",
                "delegates_to": [
                    "backend_engineer",
                    "devops_engineer",
                    "research_agent",
                ],
                "controls": [
                    "ml_pipeline_config.yaml",
                    "model_registry.json",
                    "ai_ethics_framework.md",
                ],
                "inputs": [
                    "training_datasets/",
                    "model_requirements.yaml",
                    "performance_benchmarks.json",
                ],
                "outputs": [
                    "ai_models/",
                    "ml_pipelines/",
                    "model_documentation.yaml",
                    "performance_reports.csv",
                ],
                "tools": [
                    "Python",
                    "TensorFlow",
                    "PyTorch",
                    "LangChain",
                    "OpenAI_API",
                    "HuggingFace",
                ],
                "capabilities": [
                    "ai_model_development",
                    "ml_pipeline_design",
                    "reasoning_chain_implementation",
                    "model_optimization",
                    "ai_integration",
                    "nlp_processing",
                    "computer_vision",
                    "reinforcement_learning",
                    "model_evaluation",
                ],
                "permissions": [
                    "model_training",
                    "model_deployment",
                    "ai_ethics_approval",
                ],
                "decision_making_authority": {
                    "ai_model_architecture": "final",
                    "ml_pipeline_design": "final",
                    "ai_integration_approach": "final",
                    "model_performance_thresholds": "final",
                },
                "personality": {
                    "innovative": True,
                    "analytical": True,
                    "research_oriented": True,
                    "data_driven": True,
                    "algorithm_focused": True,
                },
                "workflows": [
                    "ai_model_development_workflow",
                    "ml_pipeline_design_process",
                    "model_training_and_evaluation",
                    "ai_ethics_review_process",
                ],
                "success_metrics": [
                    "model_accuracy",
                    "ai_system_response_time",
                    "reasoning_chain_efficiency",
                    "ai_ethics_compliance_score",
                    "model_performance_metrics",
                ],
                "runtime_config": {
                    "priority": "high",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "ai_performance_impact",
                },
            },
            "builder_engineer": {
                "id": "builder_engineer",
                "title": "Spec Builder Agent",
                "mission": "Transform high-level requirements into detailed technical specifications, wireframes, and implementation guides.",
                "division": "Engineering",
                "delegates_to": [
                    "backend_engineer",
                    "frontend_engineer",
                    "product_manager",
                ],
                "controls": [
                    "specification_templates.yaml",
                    "technical_documentation_standards.md",
                    "implementation_guidelines.json",
                ],
                "inputs": [
                    "high_level_requirements.yaml",
                    "product_vision.md",
                    "technical_constraints.md",
                ],
                "outputs": [
                    "detailed_specifications.yaml",
                    "implementation_guidelines.md",
                    "technical_documentation.yaml",
                    "code_generation_spec.yaml",
                ],
                "tools": [
                    "specification_generator",
                    "documentation_builder",
                    "code_generator",
                    "requirement_analyzer",
                ],
                "capabilities": [
                    "requirement_analysis",
                    "specification_development",
                    "technical_documentation",
                    "code_generation",
                    "implementation_planning",
                    "system_design",
                    "integration_specification",
                    "quality_assurance_planning",
                    "development_workflow_definition",
                ],
                "permissions": [
                    "specification_creation",
                    "technical_documentation",
                    "implementation_guidelines",
                ],
                "decision_making_authority": {
                    "specification_approach": "final",
                    "technical_implementation": "input",
                    "code_generation_strategy": "final",
                    "implementation_guidelines": "final",
                },
                "personality": {
                    "detail_oriented": True,
                    "analytical": True,
                    "methodical": True,
                    "translation_focused": True,
                    "implementation_oriented": True,
                },
                "workflows": [
                    "requirement_analysis_process",
                    "specification_development_workflow",
                    "technical_documentation_creation",
                    "implementation_guidelines_definition",
                ],
                "success_metrics": [
                    "specification_clarity_score",
                    "implementation_guidelines_accuracy",
                    "requirement_translation_efficiency",
                    "specification_completion_rate",
                    "developer_productivity_improvement",
                ],
                "runtime_config": {
                    "priority": "high",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "specification_quality",
                },
            },
            "finance_agent": {
                "id": "finance_agent",
                "title": "Finance Agent",
                "mission": "Manage budget allocation, financial planning, cost analysis, and investment evaluation to ensure financial sustainability.",
                "division": "Operations",
                "delegates_to": ["product_manager", "cto", "coo"],
                "controls": [
                    "budget_allocation.yaml",
                    "financial_reports.json",
                    "cost_analysis_data.csv",
                ],
                "inputs": [
                    "budget_requirements.yaml",
                    "cost_projections.json",
                    "investment_proposals.md",
                ],
                "outputs": [
                    "financial_reports.json",
                    "budget_allocation.yaml",
                    "cost_analysis_data.csv",
                    "investment_recommendations.md",
                ],
                "tools": [
                    "financial_analytics_platform",
                    "budget_planning_tools",
                    "cost_analysis_software",
                    "investment_evaluator",
                ],
                "capabilities": [
                    "budget_management",
                    "financial_planning",
                    "cost_analysis",
                    "investment_evaluation",
                    "financial_risk_assessment",
                    "financial_reporting",
                    "resource_allocation",
                    "financial_forecasting",
                    "compliance_monitoring",
                ],
                "permissions": [
                    "financial_data",
                    "budget_information",
                    "cost_analysis",
                    "investment_decisions_input",
                ],
                "decision_making_authority": {
                    "budget_allocations": "input",
                    "cost_analysis": "final",
                    "financial_risk_assessment": "final",
                    "budget_recommendations": "final",
                },
                "personality": {
                    "analytical": True,
                    "detail_oriented": True,
                    "risk_aware": True,
                    "strategic": True,
                    "data_driven": True,
                },
                "workflows": [
                    "budget_allocation_process",
                    "financial_planning_workflow",
                    "cost_analysis_routine",
                    "investment_evaluation_process",
                ],
                "success_metrics": [
                    "budget_accuracy",
                    "cost_optimization_percentage",
                    "financial_risk_mitigation",
                    "return_on_investment",
                    "financial_compliance_score",
                ],
                "runtime_config": {
                    "priority": "medium",
                    "access_level": "admin",
                    "review_required": True,
                    "escalation_threshold": "financial_risk",
                },
            },
            "knowledge_architect": {
                "id": "knowledge_architect",
                "title": "Knowledge Architect Agent",
                "mission": "Organize, maintain, and optimize knowledge systems, documentation, and information architecture for the organization.",
                "division": "Operations",
                "delegates_to": ["tech_writer", "research_agent", "ops_automator"],
                "controls": [
                    "knowledge_base_schema.yaml",
                    "information_architecture.yaml",
                    "documentation_standards.md",
                ],
                "inputs": [
                    "documentation/",
                    "knowledge_assets/",
                    "information_structures.yaml",
                ],
                "outputs": [
                    "knowledge_base/",
                    "information_architecture.yaml",
                    "documentation_standards.md",
                    "knowledge_graph.json",
                ],
                "tools": [
                    "knowledge_management_system",
                    "documentation_builder",
                    "information_architect_tool",
                    "search_optimization_platform",
                ],
                "capabilities": [
                    "knowledge_management",
                    "information_architecture",
                    "documentation_systems",
                    "search_optimization",
                    "knowledge_base_maintenance",
                    "content_organization",
                    "information_classification",
                    "knowledge_graph_development",
                    "document_workflow_design",
                ],
                "permissions": [
                    "knowledge_base",
                    "documentation_systems",
                    "information_architecture",
                ],
                "decision_making_authority": {
                    "knowledge_base_structure": "final",
                    "information_architecture": "final",
                    "documentation_standards": "final",
                    "knowledge_organization": "final",
                },
                "personality": {
                    "systematic": True,
                    "organized": True,
                    "knowledge_focused": True,
                    "structure_oriented": True,
                    "optimization_minded": True,
                },
                "workflows": [
                    "knowledge_base_maintenance",
                    "information_architecture_design",
                    "documentation_organizing_process",
                    "search_optimization_workflow",
                ],
                "success_metrics": [
                    "knowledge_base_completeness",
                    "information_retrieval_accuracy",
                    "documentation_adoption_rate",
                    "knowledge_base_utilization",
                    "search_result_relevance",
                ],
                "runtime_config": {
                    "priority": "medium",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "knowledge_system_impact",
                },
            },
            "market_analyst": {
                "id": "market_analyst",
                "title": "Market Analyst Agent",
                "mission": "Conduct market research, analyze trends, user behavior, and competitive landscape to inform strategic decisions.",
                "division": "Product",
                "delegates_to": ["product_manager", "research_agent", "ux_designer"],
                "controls": [
                    "market_data_database.yaml",
                    "research_methodologies.md",
                    "competitive_analysis_framework.json",
                ],
                "inputs": [
                    "market_research_data.yaml",
                    "user_behavior_metrics.csv",
                    "competitive_analysis.json",
                ],
                "outputs": [
                    "market_analysis_report.md",
                    "trend_analysis.yaml",
                    "competitive_analysis.json",
                    "user_insight_documentation.md",
                ],
                "tools": [
                    "market_research_platform",
                    "analytics_tools",
                    "competitive_analysis_tools",
                    "data_visualization_platform",
                ],
                "capabilities": [
                    "market_research",
                    "competitive_analysis",
                    "user_behavior_analysis",
                    "trend_identification",
                    "market_forecasting",
                    "data_analytics",
                    "insight_generation",
                    "research_methodology",
                    "report_generation",
                ],
                "permissions": [
                    "market_data",
                    "research_tools",
                    "competitive_intelligence",
                    "user_analytics",
                ],
                "decision_making_authority": {
                    "market_analysis": "final",
                    "trend_identification": "final",
                    "competitive_insights": "final",
                    "research_methodology": "final",
                },
                "personality": {
                    "analytical": True,
                    "research_oriented": True,
                    "data_driven": True,
                    "trend_focused": True,
                    "insight_generation_oriented": True,
                },
                "workflows": [
                    "market_research_process",
                    "competitive_analysis_workflow",
                    "trend_analysis_routine",
                    "insight_generation_workflow",
                ],
                "success_metrics": [
                    "market_insight_accuracy",
                    "trend_prediction_success_rate",
                    "research_completeness",
                    "competitive_intelligence_quality",
                    "analysis_actionability_score",
                ],
                "runtime_config": {
                    "priority": "medium",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "strategic_impact",
                },
            },
            "meta_architect": {
                "id": "meta_architect",
                "title": "Meta Architect Agent",
                "mission": "Oversee and evolve the organization's agent definitions. Manages updates to YAML/MD schemas, validates compliance, and introduces new capabilities.",
                "division": "Governance",
                "delegates_to": [],
                "controls": [
                    "/super_agents/agents/**",
                    "/schemas/**",
                    "/specifications/**",
                ],
                "inputs": [
                    "agent_definitions.yaml",
                    "schema_updates.yaml",
                    "compliance_reports.json",
                ],
                "outputs": [
                    "schema_updates.yaml",
                    "evolution_plan.md",
                    "compliance_certificate.json",
                    "system_evolution_report.md",
                ],
                "tools": [
                    "schema_validator",
                    "compliance_checker",
                    "agent_definition_manager",
                    "system_evolution_planner",
                ],
                "capabilities": [
                    "agent_definition_management",
                    "schema_validation",
                    "compliance_monitoring",
                    "system_evolution",
                    "architecture_governance",
                    "standard_enforcement",
                    "specification_management",
                    "system_optimization",
                    "evolution_planning",
                ],
                "permissions": [
                    "admin_access",
                    "system_wide_access",
                    "definition_control",
                    "schema_management",
                ],
                "decision_making_authority": {
                    "agent_definitions": "final",
                    "system_architecture": "final",
                    "evolution_approach": "final",
                    "compliance_standards": "final",
                },
                "personality": {
                    "governance_focused": True,
                    "systematic": True,
                    "evolutionary_thinking": True,
                    "architecture_oriented": True,
                    "standard_minded": True,
                },
                "workflows": [
                    "agent_definition_review",
                    "schema_validation_process",
                    "system_evolution_planning",
                    "compliance_monitoring_workflow",
                ],
                "success_metrics": [
                    "system_evolution_success_rate",
                    "compliance_score",
                    "agent_definition_quality",
                    "system_optimization_impact",
                    "standard_enforcement_effectiveness",
                ],
                "runtime_config": {
                    "priority": "highest",
                    "access_level": "admin",
                    "review_required": False,
                    "escalation_threshold": "system_architecture_impact",
                },
            },
            "ops_automator": {
                "id": "ops_automator",
                "title": "Operations Automator Agent",
                "mission": "Create and maintain automation scripts, optimize operational workflows, and improve process efficiency.",
                "division": "Operations",
                "delegates_to": ["devops_engineer", "reliability_engineer"],
                "controls": [
                    "automation_scripts/",
                    "workflow_definitions.yaml",
                    "process_optimization_rules.json",
                ],
                "inputs": [
                    "operational_workflows.yaml",
                    "manual_processes.json",
                    "efficiency_metrics.csv",
                ],
                "outputs": [
                    "automation_scripts/",
                    "optimized_workflows.yaml",
                    "process_automation_report.md",
                    "efficiency_improvement_data.json",
                ],
                "tools": [
                    "automation_framework",
                    "workflow_engine",
                    "process_optimizer",
                    "scripting_engine",
                ],
                "capabilities": [
                    "process_automation",
                    "workflow_optimization",
                    "script_development",
                    "task_automation",
                    "efficiency_monitoring",
                    "process_analysis",
                    "automation_strategy",
                    "workflow_design",
                    "process_improvement",
                ],
                "permissions": [
                    "automation_execution",
                    "workflow_control",
                    "process_optimization",
                ],
                "decision_making_authority": {
                    "automation_approach": "final",
                    "workflow_optimization": "final",
                    "process_automation": "final",
                    "efficiency_improvements": "implementation",
                },
                "personality": {
                    "efficiency_focused": True,
                    "automation_oriented": True,
                    "process_minded": True,
                    "optimization_focused": True,
                    "systematic": True,
                },
                "workflows": [
                    "process_analysis_workflow",
                    "automation_development_process",
                    "workflow_optimization_routine",
                    "efficiency_monitoring_process",
                ],
                "success_metrics": [
                    "automation_success_rate",
                    "process_efficiency_improvement",
                    "task_automation_percentage",
                    "operational_cost_reduction",
                    "workflow_optimization_score",
                ],
                "runtime_config": {
                    "priority": "medium",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "operational_efficiency",
                },
            },
            "partnership_agent": {
                "id": "partnership_agent",
                "title": "Partnership Agent",
                "mission": "Manage external partnerships, integrations, and collaborative relationships to expand capabilities and market reach.",
                "division": "Expansion",
                "delegates_to": [
                    "product_manager",
                    "devops_engineer",
                    "security_engineer",
                ],
                "controls": [
                    "partnership_agreements.yaml",
                    "integration_specifications.json",
                    "collaboration_framework.md",
                ],
                "inputs": [
                    "partner_proposals.yaml",
                    "integration_requirements.json",
                    "partnership_opportunities.md",
                ],
                "outputs": [
                    "partnership_agreements.yaml",
                    "integration_documentation.md",
                    "collaboration_reports.json",
                    "partnership_performance_metrics.yaml",
                ],
                "tools": [
                    "partnership_management_system",
                    "integration_planner",
                    "collaboration_platform",
                    "relationship_tracker",
                ],
                "capabilities": [
                    "partnership_management",
                    "integration_development",
                    "relationship_building",
                    "collaboration_coordination",
                    "partner_evaluation",
                    "integration_strategy",
                    "relationship_maintenance",
                    "partnership_analytics",
                    "collaboration_optimization",
                ],
                "permissions": [
                    "partnership_negotiation",
                    "integration_planning",
                    "collaboration_coordination",
                ],
                "decision_making_authority": {
                    "partnership_approach": "input",
                    "integration_strategies": "final",
                    "collaboration_frameworks": "final",
                    "partner_evaluation": "final",
                },
                "personality": {
                    "collaborative": True,
                    "relationship_oriented": True,
                    "strategic": True,
                    "network_minded": True,
                    "integration_focused": True,
                },
                "workflows": [
                    "partnership_evaluation_process",
                    "integration_development_workflow",
                    "relationship_building_process",
                    "collaboration_coordination_routine",
                ],
                "success_metrics": [
                    "partnership_success_rate",
                    "integration_quality",
                    "partner_satisfaction",
                    "collaboration_efficiency",
                    "partnership_value_generation",
                ],
                "runtime_config": {
                    "priority": "medium",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "strategic_partnership_impact",
                },
            },
            "prompt_engineer": {
                "id": "prompt_engineer",
                "title": "Prompt Engineer Agent",
                "mission": "Optimize LLM prompts, develop reasoning patterns, and improve AI agent effectiveness through advanced prompt engineering.",
                "division": "Expansion",
                "delegates_to": ["ai_engineer", "research_agent"],
                "controls": [
                    "prompt_library.yaml",
                    "reasoning_patterns.json",
                    "prompt_optimization_framework.md",
                ],
                "inputs": [
                    "prompt_effectiveness_data.json",
                    "llm_performance_metrics.yaml",
                    "reasoning_chain_data.json",
                ],
                "outputs": [
                    "optimized_prompts.yaml",
                    "reasoning_patterns.json",
                    "prompt_documentation.md",
                    "effectiveness_report.json",
                ],
                "tools": [
                    "prompt_optimizer",
                    "llm_analyzer",
                    "reasoning_chain_designer",
                    "prompt_testing_framework",
                ],
                "capabilities": [
                    "prompt_optimization",
                    "reasoning_chain_design",
                    "llm_effectiveness_improvement",
                    "prompt_evaluation",
                    "reasoning_pattern_development",
                    "prompt_library_management",
                    "effectiveness_measurement",
                    "prompt_strategy_development",
                    "ai_interaction_optimization",
                ],
                "permissions": [
                    "llm_access",
                    "prompt_testing",
                    "effectiveness_measurement",
                ],
                "decision_making_authority": {
                    "prompt_optimization_approach": "final",
                    "reasoning_pattern_design": "final",
                    "prompt_strategy": "final",
                    "effectiveness_criteria": "input",
                },
                "personality": {
                    "research_oriented": True,
                    "optimization_focused": True,
                    "ai_focused": True,
                    "experimentation_oriented": True,
                    "pattern_recognition_minded": True,
                },
                "workflows": [
                    "prompt_optimization_workflow",
                    "reasoning_pattern_development",
                    "effectiveness_evaluation_process",
                    "prompt_library_maintenance",
                ],
                "success_metrics": [
                    "prompt_effectiveness_score",
                    "reasoning_chain_efficiency",
                    "llm_response_quality",
                    "prompt_optimization_success_rate",
                    "ai_interaction_improvement",
                ],
                "runtime_config": {
                    "priority": "medium",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "ai_effectiveness_impact",
                },
            },
            "reliability_engineer": {
                "id": "reliability_engineer",
                "title": "Reliability Engineer Agent",
                "mission": "Ensure system reliability, implement monitoring solutions, optimize performance, and maintain service level objectives.",
                "division": "Quality",
                "delegates_to": ["devops_engineer", "backend_engineer", "qa_engineer"],
                "controls": [
                    "monitoring_config.yaml",
                    "reliability_metrics.json",
                    "performance_benchmarks.yaml",
                ],
                "inputs": [
                    "system_logs.json",
                    "performance_metrics.csv",
                    "error_reports.yaml",
                ],
                "outputs": [
                    "reliability_report.md",
                    "monitoring_config.yaml",
                    "performance_optimization_plan.md",
                    "slo_compliance_report.yaml",
                ],
                "tools": [
                    "monitoring_platforms",
                    "performance_analyzer",
                    "error_tracking_system",
                    "reliability_analyzer",
                ],
                "capabilities": [
                    "system_reliability",
                    "performance_monitoring",
                    "error_analysis",
                    "reliability_optimization",
                    "monitoring_implementation",
                    "service_level_objectives",
                    "availability_optimization",
                    "performance_benchmarking",
                    "reliability_testing",
                ],
                "permissions": [
                    "monitoring_systems",
                    "performance_data",
                    "reliability_metrics",
                    "error_logs",
                ],
                "decision_making_authority": {
                    "reliability_standards": "final",
                    "monitoring_approach": "final",
                    "performance_optimization": "final",
                    "slo_definitions": "input",
                },
                "personality": {
                    "reliability_focused": True,
                    "performance_minded": True,
                    "detail_oriented": True,
                    "systematic": True,
                    "problem_prevention_oriented": True,
                },
                "workflows": [
                    "reliability_monitoring_process",
                    "performance_optimization_workflow",
                    "error_analysis_routine",
                    "slo_compliance_check",
                ],
                "success_metrics": [
                    "system_availability",
                    "mean_time_to_recovery",
                    "error_rate_reduction",
                    "performance_optimization_impact",
                    "slo_compliance_score",
                ],
                "runtime_config": {
                    "priority": "high",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "reliability_risk",
                },
            },
            "research_agent": {
                "id": "research_agent",
                "title": "Research Agent",
                "mission": "Conduct research, evaluate new technologies, perform proof-of-concepts, and drive innovation initiatives.",
                "division": "Expansion",
                "delegates_to": ["ai_engineer", "cto", "product_manager"],
                "controls": [
                    "research_database.yaml",
                    "innovation_pipeline.json",
                    "technology_evaluation_framework.md",
                ],
                "inputs": [
                    "research_paper_database/",
                    "technology_trends.yaml",
                    "innovation_opportunities.md",
                ],
                "outputs": [
                    "research_reports/",
                    "proof_of_concept/",
                    "innovation_proposals.md",
                    "technology_evaluation.yaml",
                ],
                "tools": [
                    "research_platform",
                    "analysis_tools",
                    "experimentation_framework",
                    "innovation_tracker",
                ],
                "capabilities": [
                    "research_conduction",
                    "technology_evaluation",
                    "proof_of_concept_development",
                    "innovation_identification",
                    "experimentation",
                    "trend_analysis",
                    "research_documentation",
                    "innovation_pipeline_management",
                    "technology_assessment",
                ],
                "permissions": [
                    "research_access",
                    "experimentation",
                    "innovation_proposal",
                    "technology_evaluation",
                ],
                "decision_making_authority": {
                    "research_approach": "final",
                    "technology_evaluation": "final",
                    "innovation_direction": "input",
                    "experimentation_approach": "final",
                },
                "personality": {
                    "research_oriented": True,
                    "innovative": True,
                    "curious": True,
                    "experimentation_focused": True,
                    "trend_aware": True,
                },
                "workflows": [
                    "research_conduction_process",
                    "technology_evaluation_workflow",
                    "proof_of_concept_development",
                    "innovation_identification_process",
                ],
                "success_metrics": [
                    "research_quality_score",
                    "innovation_success_rate",
                    "technology_evaluation_accuracy",
                    "research_implementation_rate",
                    "experimentation_success_rate",
                ],
                "runtime_config": {
                    "priority": "medium",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "innovation_impact",
                },
            },
            "tech_writer": {
                "id": "tech_writer",
                "title": "Technical Writer Agent",
                "mission": "Create comprehensive documentation, user guides, API documentation, and technical content for internal and external users.",
                "division": "Operations",
                "delegates_to": [
                    "product_manager",
                    "backend_engineer",
                    "frontend_engineer",
                ],
                "controls": [
                    "documentation_standards.md",
                    "content_management_system.yaml",
                    "style_guide.json",
                ],
                "inputs": [
                    "technical_specifications.yaml",
                    "product_features.json",
                    "user_requirements.md",
                ],
                "outputs": [
                    "documentation/",
                    "user_guides/",
                    "api_documentation/",
                    "technical_articles.md",
                    "tutorials/",
                ],
                "tools": [
                    "documentation_platform",
                    "content_management_system",
                    "api_documentation_generator",
                    "technical_editing_tools",
                ],
                "capabilities": [
                    "technical_documentation",
                    "user_guide_creation",
                    "api_documentation",
                    "content_strategy",
                    "information_architecture",
                    "content_management",
                    "technical_communication",
                    "documentation_quality_assurance",
                    "content_optimization",
                ],
                "permissions": [
                    "documentation_system",
                    "content_management",
                    "technical_information_access",
                ],
                "decision_making_authority": {
                    "documentation_approach": "final",
                    "content_strategy": "final",
                    "documentation_standards": "final",
                    "information_architecture": "input",
                },
                "personality": {
                    "communication_focused": True,
                    "detail_oriented": True,
                    "user_focused": True,
                    "clarity_oriented": True,
                    "technical_minded": True,
                },
                "workflows": [
                    "documentation_development_process",
                    "technical_writing_workflow",
                    "content_review_process",
                    "documentation_maintenance_routine",
                ],
                "success_metrics": [
                    "documentation_quality_score",
                    "user_satisfaction_with_docs",
                    "documentation_completeness",
                    "technical_accuracy_score",
                    "content_utilization_rate",
                ],
                "runtime_config": {
                    "priority": "medium",
                    "access_level": "standard",
                    "review_required": True,
                    "escalation_threshold": "documentation_quality",
                },
            },
        }

        # Create comprehensive agent spec files
        for agent_id, spec_data in comprehensive_agent_specs.items():
            filepath = os.path.join(self.agents_dir, f"{agent_id}_agent.yaml")
            with open(filepath, "w") as f:
                yaml.dump(spec_data, f, default_flow_style=False, sort_keys=False)

    def generate_agent_commands(
        self, agent_id: str, output_dir: Optional[str] = None
    ) -> bool:
        """
        Generate agent-specific command files

        Args:
            agent_id: The agent to generate commands for
            output_dir: Optional override for output directory (defaults to current working directory)

        Returns:
            True if successful, False otherwise
        """
        config = self.get_agent_config(agent_id)
        if not config:
            print(f"❌ Unknown agent: {agent_id}")
            return False

        # Determine output directory
        if output_dir is None:
            # Use current working directory as base
            output_dir = os.path.join(os.getcwd(), config["folder"])
        else:
            output_dir = os.path.join(output_dir, config["folder"])

        os.makedirs(output_dir, exist_ok=True)

        # Get default commands
        default_commands = self.registry.get("default_commands", [])

        # Load super-agent specs for context
        agent_specs = self.load_agent_specs()

        # Generate each command
        for cmd in default_commands:
            cmd_name = cmd.get("name")
            cmd_desc = cmd.get("description")
            content = self._generate_command_content(
                agent_id, cmd_name, cmd_desc, agent_specs, config
            )

            file_ext = config.get("file_extension", "md")
            filepath = os.path.join(output_dir, f"{cmd_name}.{file_ext}")

            with open(filepath, "w") as f:
                f.write(content)

            print(f"✓ Generated {cmd_name}.{file_ext} for {config['name']}")

        return True

    def _generate_command_content(
        self,
        agent_id: str,
        cmd_name: str,
        cmd_desc: str,
        agent_specs: Dict,
        agent_config: Dict,
    ) -> str:
        """Generate content for a specific command based on agent format"""
        format_type = agent_config.get("format")

        if format_type == "markdown":
            return self._generate_markdown_command(
                agent_id, cmd_name, cmd_desc, agent_specs, agent_config
            )
        elif format_type == "toml":
            return self._generate_toml_command(
                agent_id, cmd_name, cmd_desc, agent_specs, agent_config
            )
        else:
            raise ValueError(f"Unknown format: {format_type}")

    def _generate_markdown_command(
        self,
        agent_id: str,
        cmd_name: str,
        cmd_desc: str,
        agent_specs: Dict,
        agent_config: Dict,
    ) -> str:
        """Generate markdown-formatted command"""
        agent_list = self._format_agent_list(agent_specs)

        commands = {
            "super-agents-init": f"""# Super-Agents Initialization for {agent_config['name']}

You now have access to the **AICODE Labs super-agents system**. This gives you the ability to coordinate with specialized autonomous agents.

## Available Super-Agents

{agent_list}

## How to Use Super-Agents

### List Available Agents
To see all agents and their capabilities:
```
/list-agents
```

### Get Agent Help
To learn about a specific agent:
```
/agent-help backend_engineer
```

### Delegate Tasks
To assign work to a super-agent:
```
/delegate-task agent_id: Your task description here
```

Example:
```
/delegate-task backend_engineer: Design a REST API for user authentication
/delegate-task ux_designer: Create wireframes for the user dashboard
/delegate-task qa_engineer: Set up integration test suite
```

## Command Placeholders

When delegating, you can use these patterns:
- `@agent_id: task` - Synchronous delegation
- `Background: @agent_id: task` - Asynchronous delegation

## Available Commands

You have access to these super-agents commands:
- `super-agents-init` - This initialization guide
- `list-agents` - View all available agents
- `agent-help` - Get details about specific agents
- `delegate-task` - Assign work to agents
""",
            "list-agents": f"""# List Super-Agents

This command displays all available super-agents in the AICODE Labs system.

## Super-Agents Directory

{agent_list}

## Using Agent Information

Each agent has:
- **ID**: Used in delegation commands
- **Title**: Human-readable name
- **Mission**: Primary purpose and goals
- **Capabilities**: What the agent can do
- **Inputs/Outputs**: Expected data formats

To learn more about a specific agent, use:
```
/agent-help <agent_id>
```
""",
            "agent-help": f"""# Agent Help

Use this command to get detailed information about a specific super-agent.

## Syntax

```
/agent-help <agent_id>
```

## Examples

```
/agent-help ceo
/agent-help backend_engineer
/agent-help ux_designer
/agent-help security_engineer
```

## Available Agents

{agent_list}

## Agent Properties

When you query an agent, you'll get:
- **ID**: Unique identifier for delegation
- **Title**: Agent's role/title
- **Mission**: What they're designed to do
- **Capabilities**: Technical and domain expertise
- **Inputs**: What they can accept
- **Outputs**: What they produce
- **Delegates To**: Other agents they coordinate with
""",
            "delegate-task": """# Delegate Task to Super-Agent

Use this command to assign work to a super-agent and coordinate agent workflows.

## Syntax

```
/delegate-task <agent_id>: <task_description>
```

## Examples

### Simple Delegation
```
/delegate-task backend_engineer: Design a REST API for product catalog
/delegate-task ux_designer: Create mobile-responsive UI components
/delegate-task qa_engineer: Write integration tests for payment flow
```

### With Context
```
/delegate-task backend_engineer: Create user authentication endpoint
Context: Must support OAuth2 and JWT tokens
Requirements: PostgreSQL backend, async operations
```

### Sequential Delegation
```
/delegate-task product_manager: Create detailed feature specification
/delegate-task backend_engineer: Implement the feature based on spec
/delegate-task qa_engineer: Test implementation against spec
```

## Agent Selection Guide

**Executive Division** (Strategic)
- `ceo` - High-level strategy and approval
- `cto` - Technical architecture and standards
- `coo` - Operations and resource planning

**Product Division** (Requirements)
- `product_manager` - Feature specifications and roadmap
- `ux_designer` - Interface design and user experience
- `market_analyst` - Market research and user insights

**Engineering Division** (Implementation)
- `ai_engineer` - AI/ML models and reasoning chains
- `backend_engineer` - APIs, databases, services
- `frontend_engineer` - UI, web components, state management
- `devops_engineer` - Infrastructure, CI/CD, deployment
- `builder_engineer` - Code generation and scaffolding

**Quality Division** (Validation)
- `security_engineer` - Authentication, security, compliance
- `qa_engineer` - Testing, quality assurance, validation
- `reliability_engineer` - Monitoring, performance, uptime

**Operations Division** (Documentation)
- `tech_writer` - API docs, guides, documentation
- `knowledge_architect` - Knowledge base, vector memory
- `ops_automator` - Automation scripts, maintenance

**Expansion Division** (Growth)
- `finance_agent` - Budget, costs, resource allocation
- `partnership_agent` - Integrations, partnerships
- `prompt_engineer` - LLM optimization, prompt engineering
- `research_agent` - New models, techniques, R&D

**Governance Division** (Oversight)
- `meta_architect` - Compliance, architecture validation

## Task Best Practices

1. **Be Specific**: Clear requirements produce better results
2. **Provide Context**: Include relevant constraints and examples
3. **Reference Specs**: Link to existing specifications when relevant
4. **Sequential Tasks**: Use multiple delegations for complex work
5. **Validation**: Ask `qa_engineer` to review critical work
""",
        }

        content = commands.get(cmd_name, f"# {cmd_name}\n\n{cmd_desc}")

        return content

    def _generate_toml_command(
        self,
        agent_id: str,
        cmd_name: str,
        cmd_desc: str,
        agent_specs: Dict,
        agent_config: Dict,
    ) -> str:
        """Generate TOML-formatted command"""
        agent_list = self._format_agent_list_toml(agent_specs)

        commands = {
            "super-agents-init": f"""description = "Initialize connection to AICODE Labs super-agents"

prompt = \"\"\"
You now have access to the AICODE Labs super-agents system.

Available super-agents:
{agent_list}

To use super-agents:
1. List agents: /list-agents
2. Get agent info: /agent-help <agent_id>
3. Delegate work: /delegate-task <agent_id>: <task>

Examples:
/delegate-task backend_engineer: Design authentication API
/delegate-task ux_designer: Create mobile UI mockups
/delegate-task qa_engineer: Set up test framework
\"\"\"
""",
            "list-agents": f"""description = "List all available super-agents"

prompt = \"\"\"
Super-Agents Directory:
{agent_list}

Use /agent-help <agent_id> to learn more about specific agents.
\"\"\"
""",
            "agent-help": f"""description = "Get help about a specific super-agent"

prompt = \"\"\"
Available agents:
{agent_list}

Usage: /agent-help <agent_id>

Examples:
/agent-help ceo
/agent-help backend_engineer
/agent-help security_engineer
\"\"\"
""",
            "delegate-task": f"""description = "Delegate a task to a super-agent"

prompt = \"\"\"
Delegate work to super-agents using:
/delegate-task <agent_id>: <task description>

Examples:
/delegate-task backend_engineer: Create API for product catalog
/delegate-task ux_designer: Design dashboard interface
/delegate-task qa_engineer: Write integration tests

Available agents:
{agent_list}
\"\"\"
""",
        }

        content = commands.get(
            cmd_name, f"""description = "{cmd_desc}"\nprompt = """ """ """
        )

        return content

    def _format_agent_list(self, agent_specs: Dict) -> str:
        """Format agent list for markdown output"""
        if not agent_specs:
            return "No agents found. Run orchestrator to load agent specifications."

        lines = []
        divisions = {}

        # Group agents by division
        for agent_id, spec in agent_specs.items():
            division = spec.get("division", "Other")
            if division not in divisions:
                divisions[division] = []
            divisions[division].append((agent_id, spec))

        # Format by division
        for division in sorted(divisions.keys()):
            lines.append(f"### {division}")
            lines.append("")

            for agent_id, spec in sorted(divisions[division]):
                title = spec.get("title", agent_id)
                mission = (
                    spec.get("mission", "").split(".")[0]
                    if spec.get("mission")
                    else "No mission defined"
                )

                # Add more comprehensive information if available
                capabilities = spec.get("capabilities", [])
                tools = spec.get("tools", [])

                agent_info = f"- **`{agent_id}`** ({title}): {mission}"

                # Add capabilities if they exist and aren't too long
                if capabilities:
                    cap_list = ", ".join(capabilities[:3])  # Show first 3 capabilities
                    if len(capabilities) > 3:
                        cap_list += f" (+{len(capabilities)-3} more)"
                    agent_info += f"\n  - *Capabilities*: {cap_list}"

                # Add tools if they exist
                if tools:
                    tool_list = ", ".join(
                        [str(t) for t in tools[:3]]
                    )  # Show first 3 tools
                    if len(tools) > 3:
                        tool_list += f" (+{len(tools)-3} more)"
                    agent_info += f"\n  - *Tools*: {tool_list}"

                lines.append(agent_info)
                lines.append("")

        return "\n".join(lines)

    def _format_agent_list_toml(self, agent_specs: Dict) -> str:
        """Format agent list for TOML output"""
        if not agent_specs:
            return "No agents loaded"

        lines = []
        for agent_id, spec in sorted(agent_specs.items()):
            title = spec.get("title", agent_id)
            mission = (
                spec.get("mission", "").split(".")[0]
                if spec.get("mission")
                else "No mission defined"
            )

            # Create a more descriptive entry
            capabilities = spec.get("capabilities", [])
            tools = spec.get("tools", [])

            description_parts = [mission]
            if capabilities:
                description_parts.append(f"Capabilities: {', '.join(capabilities[:2])}")
            if tools:
                description_parts.append(
                    f"Tools: {', '.join([str(t) for t in tools[:2]])}"
                )

            description = " | ".join(description_parts)
            lines.append(f"- {agent_id}: {title} - {description}")

        return "\n".join(lines)

    def initialize_for_agent(
        self, agent_id: str, output_dir: Optional[str] = None
    ) -> bool:
        """
        Full initialization for a specific agent

        Args:
            agent_id: The agent to initialize for
            output_dir: Optional directory to output files (defaults to current working directory)

        Returns:
            True if successful
        """
        config = self.get_agent_config(agent_id)
        if not config:
            print(f"❌ Unknown agent: {agent_id}")
            return False

        print(f"\n🤖 Initializing Super-Agents for {config['name']}...")

        # Determine output directory - use provided directory or default to current working directory
        if output_dir is None:
            output_dir = os.getcwd()

        # Generate agent-specific commands with the specified output directory
        if not self.generate_agent_commands(agent_id, output_dir):
            return False

        # Create comprehensive agent initialization files with output directory
        self._create_agent_initialization_files(agent_id, output_dir)

        folder = config["folder"]
        actual_output_path = os.path.join(output_dir, folder)
        print(f"✓ Super-agents initialized in {actual_output_path}")
        print("\nNext steps:")
        print(
            f"  1. Open {actual_output_path}super-agents-init.{config['file_extension']}"
        )
        print(f"  2. Use commands in your {config['name']} environment")
        print("  3. Start delegating tasks to super-agents!\n")

        return True

    def _create_comprehensive_context_files(self, superagents_dir: str, agent_id: str):
        """Create comprehensive context files for superagents workflow"""
        from datetime import datetime

        # Load all agent specs to provide complete context
        all_agent_specs = self.load_agent_specs()

        # Create main context files in .superagents directory
        context_files = {
            "SYSTEM_CONTEXT.md": f"""# AICODE Labs Super-Agents System Context

## System Overview
- **System Name**: AICODE Labs Super-Agents
- **Version**: 2.0
- **Initialization Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Active Agent**: {agent_id}

## Architecture
The system consists of specialized AI agents with cognitive reasoning capabilities, autonomous learning, and coordinated workflows.

## Core Principles
1. **Delegation**: Tasks are automatically routed to appropriate specialized agents
2. **Coordination**: Agents collaborate following established communication patterns
3. **Learning**: Agents continuously improve based on task outcomes
4. **Governance**: All activities follow compliance and approval workflows
""",
            "AGENT_REGISTRY.md": self._generate_agent_registry_markdown(
                all_agent_specs
            ),
            "DELEGATION_WORKFLOWS.md": """# Super-Agents Delegation Workflows

## Automatic Routing Rules
When a task matches specific criteria, it is automatically delegated:

### Backend/API Work
- **Trigger**: API design, database schemas, server logic
- **Agent**: `backend_engineer`
- **Capabilities**: API development, database design, business logic

### Frontend/UI Work
- **Trigger**: UI components, user interfaces, client-side logic
- **Agent**: `frontend_engineer`
- **Capabilities**: UI frameworks, state management, accessibility

### Full-Stack Features
- **Trigger**: End-to-end feature development
- **Agent**: `fullstack_engineer`
- **Capabilities**: Both frontend and backend coordination

### Infrastructure/DevOps
- **Trigger**: Deployment, CI/CD, cloud infrastructure
- **Agent**: `devops_engineer`
- **Capabilities**: Containerization, infrastructure-as-code

### Security
- **Trigger**: Security reviews, vulnerability assessment
- **Agent**: `security_engineer`
- **Capabilities**: Security analysis, compliance checking

### Quality Assurance
- **Trigger**: Testing, quality validation
- **Agent**: `qa_engineer`
- **Capabilities**: Test automation, quality metrics

## Manual Delegation
For tasks not matching automatic rules, use:
```
/delegate-task [agent_id]: [task_description]
```

## Multi-Agent Workflows
Complex tasks may involve multiple agents sequentially:
1. Product definition → `product_manager`
2. Design → `ux_designer`
3. Backend implementation → `backend_engineer`
4. Frontend implementation → `frontend_engineer`
5. Security review → `security_engineer`
6. Quality validation → `qa_engineer`
7. Deployment → `devops_engineer`
""",
            "COMMUNICATION_PROTOCOL.md": """# Agent Communication Protocol

## Message Format
Agents communicate using structured messages:
```
[AGENT_ID] [TASK_STATUS]: [DESCRIPTION]
- Capabilities Used: [LIST]
- Decisions Made: [LIST]
- Dependencies: [LIST]
- Next Steps: [LIST]
```

## Coordination Patterns
- **Sequential**: One agent completes, triggers next agent
- **Parallel**: Multiple agents work simultaneously on different aspects
- **Review**: Work sent for quality/approval review
- **Escalation**: Complex issues escalated to senior agents

## Status Tracking
- `initialized`: Task received, preparation
- `working`: Active task execution
- `review`: Awaiting review/approval
- `completed`: Task finished successfully
- `blocked`: Awaiting input or resolution
- `failed`: Task could not be completed
""",
            "EXECUTION_GUIDELINES.md": """# Agent Execution Guidelines

## Task Execution Process
1. **Analysis**: Understand task requirements
2. **Planning**: Determine approach and resources
3. **Execution**: Perform required work
4. **Validation**: Verify correctness and quality
5. **Reporting**: Document results and next steps

## Quality Standards
- Follow best practices for the domain
- Maintain consistency with existing codebase
- Include appropriate documentation
- Consider performance and security implications
- Provide clear error handling

## Collaboration Rules
- Share relevant context when delegating
- Maintain clear communication
- Update status regularly for long tasks
- Escalate issues appropriately
- Document important decisions
""",
            "KNOWLEDGE_BASE.md": self._generate_knowledge_base(all_agent_specs),
            "COMPANY_STRATEGY.md": """# AICODE Labs Company Strategy

## Mission
To provide autonomous AI agent solutions that accelerate software development while maintaining quality and governance.

## Vision
To create a self-organizing AI workforce that can deliver complete software projects with minimal human intervention.

## Values
- **Automation**: Maximize automated task execution
- **Quality**: Maintain high standards across all deliverables
- **Transparency**: Provide clear visibility into all processes
- **Collaboration**: Foster effective agent-to-agent coordination
- **Learning**: Continuously improve based on experience
""",
            "RUNTIME_CONFIG.md": """# Runtime Configuration

## Lifecycle Management
- **Startup Order**: Meta Architect → CEO → CTO → COO → Specialized Engineers
- **Health Checks**: Performed every 30 seconds
- **Restart Policy**: Always restart on failure

## Governance Settings
- Human review required for production deployment
- Approval thresholds for different environments
- Audit logging enabled
- Compliance checking active

## Resource Allocation
- Executive agents: 4GB RAM
- Engineering agents: 8GB RAM
- AI agents: 12GB RAM
- Support agents: 2GB RAM

## Cognitive Reasoning
- Reflection performed daily
- Decision weighting by role priority
- Conflict resolution via majority voting
""",
        }

        for filename, content in context_files.items():
            filepath = os.path.join(superagents_dir, filename)
            with open(filepath, "w") as f:
                f.write(content)

        # Create divisions directory with division-specific context
        divisions_dir = os.path.join(superagents_dir, "divisions")
        os.makedirs(divisions_dir, exist_ok=True)

        for division in [
            "Executive",
            "Product",
            "Engineering",
            "Quality",
            "Operations",
            "Expansion",
            "Governance",
        ]:
            division_file = os.path.join(
                divisions_dir, f"{division.lower()}_guidelines.md"
            )
            with open(division_file, "w") as f:
                f.write(
                    f"""# {division} Division Guidelines

## Role and Responsibilities
Agents in the {division} division are responsible for:

## Decision-Making Authority
- Level 1 decisions: [specify]
- Level 2 decisions: [specify]
- Escalation requirements: [specify]

## Coordination Requirements
- Required consultations: [specify]
- Reporting obligations: [specify]
- Communication protocols: [specify]
"""
                )

        print("  ✓ Created comprehensive context files in .superagents directory")

    def _generate_agent_registry_markdown(self, agent_specs: Dict) -> str:
        """Generate agent registry in markdown format"""
        lines = ["# Super-Agent Registry", ""]

        divisions = {}
        for agent_id, spec in agent_specs.items():
            division = spec.get("division", "Other")
            if division not in divisions:
                divisions[division] = []
            divisions[division].append((agent_id, spec))

        for division, agents in divisions.items():
            lines.append(f"## {division} Division")
            lines.append("")

            for agent_id, spec in sorted(agents):
                lines.append(f"### {agent_id}")
                lines.append(f"- **Title**: {spec.get('title', 'N/A')}")
                lines.append(f"- **Mission**: {spec.get('mission', 'N/A')}")
                lines.append(
                    f"- **Capabilities**: {', '.join(spec.get('capabilities', []))}"
                )
                lines.append(f"- **Tools**: {', '.join(spec.get('tools', []))}")
                lines.append(f"- **Inputs**: {', '.join(spec.get('inputs', []))}")
                lines.append(f"- **Outputs**: {', '.join(spec.get('outputs', []))}")
                lines.append("")

        return "\n".join(lines)

    def _generate_knowledge_base(self, agent_specs: Dict) -> str:
        """Generate knowledge base with all agent capabilities"""
        lines = [
            "# Super-Agents Knowledge Base",
            "",
            "## System Capabilities",
            "The AICODE Labs system can handle complex software development tasks through specialized agents.",
            "",
            "## Available Specialized Agents",
            "",
        ]

        for agent_id, spec in sorted(agent_specs.items()):
            lines.append(f"### {agent_id}")
            lines.append(f"**Title**: {spec.get('title', 'N/A')}")
            lines.append(f"**Mission**: {spec.get('mission', 'N/A')}")
            if spec.get("capabilities"):
                lines.append("**Capabilities**:")
                for cap in spec["capabilities"]:
                    lines.append(f"- {cap}")
            lines.append("")

        lines.extend(
            [
                "## Cognitive Reasoning",
                "Agents apply cognitive reasoning including daily reflection, decision weighting, and conflict resolution.",
                "",
                "## Autonomous Learning",
                "Agents continuously improve through experience, learning from task outcomes and feedback.",
                "",
                "## Governance & Compliance",
                "All agent activities follow governance protocols with appropriate approval requirements.",
                "",
            ]
        )

        return "\n".join(lines)

    def _create_agent_initialization_files(
        self, agent_id: str, output_dir: Optional[str] = None
    ):
        """
        Create comprehensive initialization files for the selected agent
        including project context, agent specs, and other necessary resources
        """
        config = self.get_agent_config(agent_id)

        # Create the main .superagents directory structure at project root level
        superagents_dir = os.path.join(output_dir or os.getcwd(), ".superagents")
        os.makedirs(superagents_dir, exist_ok=True)

        # Create comprehensive superagents context
        self._create_comprehensive_context_files(superagents_dir, agent_id)

        # Determine the agent-specific output directory (where command files go)
        if output_dir is None:
            agent_output_dir = os.path.join(self.agents_dir, config["folder"])
        else:
            agent_output_dir = os.path.join(output_dir, config["folder"])
        os.makedirs(agent_output_dir, exist_ok=True)

        # Load super-agent specs
        agent_specs = self.load_agent_specs()
        selected_agent_spec = agent_specs.get(agent_id)

        # Create agent profile file
        agent_profile_path = os.path.join(agent_output_dir, "agent_profile.yaml")
        with open(agent_profile_path, "w") as f:
            import yaml

            yaml.dump(
                {
                    "id": agent_id,
                    "name": config["name"],
                    "format": config["format"],
                    "folder": config["folder"],
                    "specification": selected_agent_spec or {},
                },
                f,
            )

        # Create context directory
        context_dir = os.path.join(agent_output_dir, "context")
        os.makedirs(context_dir, exist_ok=True)

        # Create project context file
        project_context_path = os.path.join(context_dir, "project_context.json")
        with open(project_context_path, "w") as f:
            import json

            project_context = {
                "project_name": "Default Project",
                "project_description": "AICODE Labs project",
                "timeline": {
                    "start_date": "2025-01-01",
                    "end_date": "2025-12-31",
                    "milestones": [],
                },
                "resources": {
                    "budget": "TBD",
                    "allocated_agents": [agent_id],
                    "tools": [config.get("cli_tool", "unknown")],
                },
                "status": "initialized",
            }
            json.dump(project_context, f, indent=2)

        # Create shared memories directory
        shared_memories_dir = os.path.join(context_dir, "shared_memories")
        os.makedirs(shared_memories_dir, exist_ok=True)

        # Create agent-specific memories directory
        agent_memories_dir = os.path.join(context_dir, "agent_memories")
        os.makedirs(agent_memories_dir, exist_ok=True)

        # Create specs directory
        specs_dir = os.path.join(agent_output_dir, "specs")
        os.makedirs(specs_dir, exist_ok=True)

        # Create agent specs file
        agent_specs_path = os.path.join(specs_dir, "agent_specs.yaml")
        with open(agent_specs_path, "w") as f:
            import yaml

            yaml.dump(selected_agent_spec or {}, f)

        # Create task requirements template
        task_requirements_path = os.path.join(specs_dir, "task_requirements.md")
        with open(task_requirements_path, "w") as f:
            f.write(
                f"""# Task Requirements for {agent_id}

## Current Task Context

This section provides context for your current task assignment.

### Task Definition
- **Agent Id**: {agent_id}
- **Agent Name**: {config['name']}
- **Agent Mission**: {(selected_agent_spec or {}).get('mission', 'N/A')}

### Capabilities to Utilize
{(selected_agent_spec or {}).get('capabilities', [])}

### Required Outputs
Based on your specifications, please produce relevant outputs for your role.

### Success Criteria
- Complete the assigned task effectively
- Follow established patterns and guidelines
- Provide comprehensive documentation
- Ensure quality and best practices
"""
            )

        # Create resources directory
        resources_dir = os.path.join(agent_output_dir, "resources")
        os.makedirs(resources_dir, exist_ok=True)

        # Create tools file
        tools_path = os.path.join(resources_dir, "tools.json")
        with open(tools_path, "w") as f:
            import json

            tools = {
                "primary_cli": config.get("cli_tool", "unknown"),
                "file_extensions": [config.get("file_extension", "txt")],
                "available_commands": [
                    cmd["name"] for cmd in self.registry.get("default_commands", [])
                ],
            }
            json.dump(tools, f, indent=2)

        # Create dependencies file
        dependencies_path = os.path.join(resources_dir, "dependencies.txt")
        with open(dependencies_path, "w") as f:
            f.write(
                f"""# Dependencies for {agent_id}

## Required Tools
- {config.get("cli_tool", "unknown") or "None specified"}

## Required Knowledge
- AICODE Labs agent system
- YAML/JSON configuration
- Agent communication protocols
- Task-specific requirements

## Project Dependencies
- Agent registry
- Agent specifications
- Context files
- Output specifications
"""
            )

        # Create workflows directory
        workflows_dir = os.path.join(agent_output_dir, "workflows")
        os.makedirs(workflows_dir, exist_ok=True)

        # Create standard operating procedures
        sop_path = os.path.join(workflows_dir, "standard_operating_procedures.md")
        with open(sop_path, "w") as f:
            f.write(
                f"""# Standard Operating Procedures for {agent_id}

## Role-Specific Procedures

As a {config['name']} agent, you should follow these procedures when working within the AICODE Labs system:

### 1. Task Acceptance
- Review the task requirements in task_requirements.md
- Verify your capabilities align with the task
- Accept the task in your work queue

### 2. Context Integration
- Study the project context in the context/ directory
- Understand dependencies and constraints
- Consider collaboration with other agents

### 3. Execution Process
- Follow your role-specific guidelines
- Maintain proper documentation
- Adhere to quality standards
- Comply with security policies

### 4. Output Generation
- Generate outputs according to your agent specifications
- Update the knowledge base with relevant information
- Create proper documentation for other agents
- Follow the established output format

### 5. Collaboration Protocol
- Communicate status updates as needed
- Request help when facing blockers
- Share relevant insights with the team
- Follow the delegation and communication protocols
"""
            )

        # Create collaboration guidelines
        guidelines_path = os.path.join(workflows_dir, "collaboration_guidelines.md")
        with open(guidelines_path, "w") as f:
            f.write(
                f"""# Collaboration Guidelines for {agent_id}

## Working with Other Agents

As a {config['name']} agent, you may need to collaborate with other agents in the AICODE Labs system:

### Direct Collaborators
{(selected_agent_spec or {}).get('delegates_to', []) or 'No specific delegates defined'}

### Communication Protocol
- Use the established agent communication patterns
- Share relevant context when delegating
- Maintain clear documentation
- Follow up on delegated tasks appropriately

### Information Sharing
- Update the shared knowledge base with relevant information
- Document decisions and rationale
- Share insights that may benefit other agents
- Maintain proper access controls for sensitive information
"""
            )

        # Create templates directory
        templates_dir = os.path.join(agent_output_dir, "templates")
        os.makedirs(templates_dir, exist_ok=True)

        # Create response template for the agent
        response_template_path = os.path.join(templates_dir, "response_template.md")
        with open(response_template_path, "w") as f:
            f.write(
                f"""# Response Template for {agent_id}

## Structure for {config['name']} Agent Responses

When responding to tasks as a {config['name']} agent, structure your responses using this template:

### Task Completion Summary
- **Task**: [Brief description of the completed task]
- **Status**: [Completed/In Progress/Blocked]
- **Time Taken**: [Estimated time]

### Implementation Details
[Provide specific implementation details relevant to your role]

### Key Decisions Made
[List important decisions made during implementation]

### Dependencies and Prerequisites
[Identify any dependencies or prerequisites for this work]

### Outputs Created
[List of files, documents, or artifacts created]

### Next Steps
[Recommendations for next steps or follow-up actions]

### Potential Improvements
[Suggestions for future improvements or optimizations]

---

### For Executive Agents (CEO, CTO, COO):
- Focus on strategic alignment
- Include resource implications
- Address risk management
- Provide approval status

### For Engineering Agents (Backend, Frontend, AI, DevOps):
- Detail technical implementation
- Document architecture decisions
- Specify performance considerations
- Outline integration points

### For Product Agents (Product Manager, UX Designer):
- Emphasize user needs
- Document design decisions
- Specify success metrics
- Outline validation approach

### For Quality Agents (QA, Reliability):
- Detail testing approach
- Document test results
- Specify performance metrics
- Outline monitoring setup
"""
            )

        # Create division-specific files based on the selected agent
        if selected_agent_spec:
            division = selected_agent_spec.get("division", "Other")

            division_dir = os.path.join(agent_output_dir, "division_specific")
            os.makedirs(division_dir, exist_ok=True)

            # Create division-specific context
            division_context_path = os.path.join(
                division_dir, f"{division.lower()}_context.md"
            )
            with open(division_context_path, "w") as f:
                f.write(
                    f"""# Division Context: {division}

## Role within {division} Division

As an agent in the {division} division, you are expected to:

### Primary Responsibilities
- {(selected_agent_spec or {}).get('mission', 'No mission specified')}

### Key Capabilities
"""
                )
                for capability in (selected_agent_spec or {}).get("capabilities", []):
                    f.write(f"- {capability}\n")

                f.write(
                    """
### Tools and Technologies
"""
                )
                for tool in (selected_agent_spec or {}).get("tools", []):
                    f.write(f"- {tool}\n")

                f.write(
                    """
### Input Requirements
"""
                )
                for input_type in (selected_agent_spec or {}).get("inputs", []):
                    f.write(f"- {input_type}\n")

                f.write(
                    """
### Expected Outputs
"""
                )
                for output_type in (selected_agent_spec or {}).get("outputs", []):
                    f.write(f"- {output_type}\n")

        print(f"  ✓ Created comprehensive initialization files for {agent_id}")

    def initialize_for_all_available(self) -> int:
        """
        Initialize for all available agents

        Returns:
            Number of agents initialized
        """
        available = self.get_available_agents()
        count = 0

        print(
            f"\n🤖 Initializing Super-Agents for {len(available)} available agents...\n"
        )

        for agent_id in available:
            if self.generate_agent_commands(agent_id):
                count += 1

        print(f"\n✓ Successfully initialized {count} agents\n")
        return count

    def create_agent_context_file(self, agent_id: str) -> bool:
        """
        Create a unified context file for an agent with all specs

        Args:
            agent_id: The agent to create context for

        Returns:
            True if successful
        """
        config = self.get_agent_config(agent_id)
        if not config:
            return False

        output_dir = os.path.join(os.path.dirname(self.agents_dir), config["folder"])
        os.makedirs(output_dir, exist_ok=True)

        agent_specs = self.load_agent_specs()

        # Create context file
        filepath = os.path.join(output_dir, "super-agents-context.yaml")

        context = {
            "agent_system": "AICODE Labs Super-Agents",
            "external_agent": {
                "id": agent_id,
                "name": config["name"],
                "format": config["format"],
            },
            "super_agents": agent_specs,
        }

        with open(filepath, "w") as f:
            yaml.dump(context, f, default_flow_style=False, sort_keys=False)

        print(f"✓ Created context file: {filepath}")
        return True

    def inject_delegation_prompt_to_agent(self, agent_id: str, output_dir: str) -> bool:
        """
        Inject the delegation prompt to a specific agent's command files.

        Args:
            agent_id: The agent to inject the delegation prompt to
            output_dir: Output directory for the delegation file

        Returns:
            True if successful
        """
        if not self.delegation_generator:
            return False

        try:
            # Create agent-specific output directory
            config = self.get_agent_config(agent_id)
            if not config:
                return False

            agent_output_dir = os.path.join(output_dir, config["folder"])
            os.makedirs(agent_output_dir, exist_ok=True)

            # Generate and save the delegation prompt
            delegation_content = (
                self.delegation_generator.generate_agent_specific_context(agent_id)
            )
            delegation_file = os.path.join(agent_output_dir, "automatic_delegation.md")

            with open(delegation_file, "w") as f:
                f.write(delegation_content)

            return True
        except Exception:
            return False

    def track_execution_start(self, agent_id: str, task_description: str):
        """
        Start tracking an execution through the execution tracker.

        Args:
            agent_id: The agent performing the execution
            task_description: Description of the task being executed

        Returns:
            Execution ID if successful, None otherwise
        """
        if not self.execution_tracker:
            return None

        try:
            return self.execution_tracker.start_execution(agent_id, task_description)
        except Exception:
            return None

    def track_execution_tool(self, tool_name: str, description: str):
        """
        Record tool usage in the execution tracker.

        Args:
            tool_name: Name of the tool used
            description: Description of how the tool was used
        """
        if self.execution_tracker:
            try:
                self.execution_tracker.record_tool_usage(tool_name, description)
            except Exception:
                pass

    def track_execution_decision(self, decision: str, reasoning: str):
        """
        Record a decision in the execution tracker.

        Args:
            decision: The decision made
            reasoning: Reasoning behind the decision
        """
        if self.execution_tracker:
            try:
                self.execution_tracker.record_decision(decision, reasoning)
            except Exception:
                pass

    def track_execution_blocker(self, blocker: str, resolution: str):
        """
        Record a blocker in the execution tracker.

        Args:
            blocker: Description of the blocker
            resolution: How it was resolved
        """
        if self.execution_tracker:
            try:
                self.execution_tracker.record_blocker(blocker, resolution)
            except Exception:
                pass

    def track_execution_output(self, output_file: str, description: str):
        """
        Record an output in the execution tracker.

        Args:
            output_file: Name/path of the output file
            description: Description of the output
        """
        if self.execution_tracker:
            try:
                self.execution_tracker.record_output(output_file, description)
            except Exception:
                pass

    def track_execution_metrics(self, **metrics):
        """
        Record metrics in the execution tracker.

        Args:
            **metrics: Arbitrary metrics to track
        """
        if self.execution_tracker:
            try:
                self.execution_tracker.record_metrics(**metrics)
            except Exception:
                pass

    def end_execution_and_learn(self, agent_id: str, status: str, result: Dict):
        """
        Complete an execution and run the learning cycle.

        Args:
            agent_id: The agent that performed the execution
            status: Status of the execution
            result: Result of the execution

        Returns:
            Dict with learning results
        """
        if not all([self.execution_tracker, self.reflection_agent, self.spec_manager]):
            return {
                "success": False,
                "agent_id": agent_id,
                "learnings": None,
                "changes": None,
            }

        try:
            # End the execution
            self.execution_tracker.end_execution(status, result)

            # Export execution data for reflection
            execution_data = self.execution_tracker.export_for_reflection(agent_id)

            # Analyze the executions to extract learnings
            learnings = self.reflection_agent.analyze_executions(
                agent_id, execution_data
            )

            # Load the current agent spec
            current_spec = self.spec_manager.load_agent_spec(agent_id)

            # Generate updated spec based on learnings
            updated_spec = self.reflection_agent.generate_spec_update(
                current_spec, learnings
            )

            # Validate the changes
            validation = self.reflection_agent.validate_spec_changes(
                current_spec, updated_spec
            )

            # Save the updated spec
            save_result = self.spec_manager.save_agent_spec(agent_id, updated_spec)

            return {
                "success": save_result,
                "agent_id": agent_id,
                "learnings": learnings,
                "changes": updated_spec,
                "validation": validation,
            }
        except Exception as e:
            return {
                "success": False,
                "agent_id": agent_id,
                "learnings": None,
                "changes": None,
                "error": str(e),
            }
