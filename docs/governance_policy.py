#!/usr/bin/env python3
"""
Governance and security policy module for super-agents system

Implements governance policies and procedures for:
- Access control and authentication
- Authorization policies
- Data handling policies
- Privacy and compliance
- Risk management
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


class GovernancePolicy:
    """
    Governance and security policy management for super-agents system
    
    Defines policies for:
    - Access control
    - Authorization
    - Data handling
    - Privacy compliance
    - Risk management
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize governance policy configuration
        
        Args:
            config_dir: Directory for governance configuration files
        """
        if config_dir is None:
            config_dir = os.path.join(os.getcwd(), "config")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Policy files
        self.policy_file = self.config_dir / "governance_policy.json"
        self.compliance_log = self.config_dir / "compliance_log.json"
        
        # Initialize default governance policies
        self._initialize_governance_policies()
    
    def _initialize_governance_policies(self):
        """Initialize default governance policies"""
        if not self.policy_file.exists():
            default_policies = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "access_control": {
                    "require_authentication": True,
                    "minimum_password_strength": "medium",
                    "password_expiration_days": 90,
                    "failed_login_lockout_threshold": 3,
                    "session_timeout_minutes": 60,
                    "two_factor_authentication_required": False
                },
                "authorization": {
                    "role_based_access_control": True,
                    "principle_least_privilege": True,
                    "privilege_escalation_procedures": [
                        "approval_required",
                        "time_limited",
                        "audit_trail"
                    ],
                    "access_reviews_frequency": "monthly"
                },
                "data_handling": {
                    "classification_levels": ["public", "internal", "confidential", "restricted"],
                    "encryption_at_rest_required": True,
                    "encryption_in_transit_required": True,
                    "data_retention_period_days": 365,
                    "data_deletion_procedures": ["secure_erase", "verification"],
                    "data_breach_notification_hours": 24
                },
                "privacy_compliance": {
                    "gdpr_compliant": True,
                    "ccpa_compliant": True,
                    "data_minimization_required": True,
                    "consent_management_enabled": True,
                    "right_to_access_procedures": True,
                    "right_to_erasure_procedures": True
                },
                "compliance_monitoring": {
                    "audit_logging_required": True,
                    "compliance_scanning_frequency": "daily",
                    "policy_violation_reporting": "immediate",
                    "compliance_dashboard_enabled": True
                },
                "risk_management": {
                    "risk_assessment_frequency": "quarterly",
                    "threat_modeling_required": True,
                    "vulnerability_scanning_enabled": True,
                    "incident_response_plan_mandatory": True
                }
            }
            
            with open(self.policy_file, "w") as f:
                json.dump(default_policies, f, indent=2)
    
    def get_policy(self, policy_section: str = None) -> Dict[str, Any]:
        """
        Get governance policy configuration
        
        Args:
            policy_section: Specific section to retrieve (all if None)
            
        Returns:
            Policy configuration
        """
        with open(self.policy_file, "r") as f:
            policies = json.load(f)
        
        if policy_section:
            return policies.get(policy_section, {})
        return policies
    
    def update_policy(self, policy_section: str, policy_value: Any) -> bool:
        """
        Update governance policy configuration
        
        Args:
            policy_section: Section to update (e.g., "access_control")
            policy_value: New policy value
            
        Returns:
            True if update succeeds
        """
        try:
            with open(self.policy_file, "r") as f:
                policies = json.load(f)
            
            policies[policy_section] = policy_value
            policies["last_updated"] = datetime.now().isoformat()
            
            with open(self.policy_file, "w") as f:
                json.dump(policies, f, indent=2)
            
            # Log policy update
            self._log_compliance_event("policy_update", {
                "section": policy_section,
                "timestamp": policies["last_updated"]
            })
            
            return True
        except Exception as e:
            print(f"Error updating policy: {e}")
            return False
    
    def validate_access_request(self, user_id: str, resource: str, action: str) -> Dict[str, bool]:
        """
        Validate an access request against governance policies
        
        Args:
            user_id: ID of requesting user
            resource: Resource requested
            action: Action requested
            
        Returns:
            Dict with validation results
        """
        policy = self.get_policy("authorization")
        
        result = {
            "authorized": False,
            "requires_approval": False,
            "requires_mfa": False,
            "valid_user": self._validate_user(user_id),
            "valid_resource": self._validate_resource(resource),
            "policy_compliant": True  # Simplified for example
        }
        
        # Check if MFA is required based on policy
        if policy.get("two_factor_authentication_required", False):
            result["requires_mfa"] = True
        
        # More sophisticated authorization logic would go here
        # including role-based checks, privilege escalation procedures, etc.
        
        # For demo purposes, allow access if user and resource are valid
        if result["valid_user"] and result["valid_resource"]:
            result["authorized"] = True
        
        return result
    
    def _validate_user(self, user_id: str) -> bool:
        """
        Validate user identity
        
        Args:
            user_id: User identifier to validate
            
        Returns:
            True if user is valid
        """
        # In practice, this would check against user directory/database
        # For demo, accept any non-empty user ID
        return bool(user_id.strip())
    
    def _validate_resource(self, resource: str) -> bool:
        """
        Validate resource access
        
        Args:
            resource: Resource identifier to validate
            
        Returns:
            True if resource is valid
        """
        # In practice, this would check against resource directory/database
        # For demo, accept any non-empty resource
        return bool(resource.strip())
    
    def classify_data(self, data: str, context: str = "") -> str:
        """
        Classify data according to governance policies
        
        Args:
            data: Data to classify
            context: Context for classification
            
        Returns:
            Classification level
        """
        policy = self.get_policy("data_handling")
        levels = policy.get("classification_levels", ["public", "internal", "confidential", "restricted"])
        
        # Simple classification based on content analysis
        data_lower = data.lower()
        context_lower = context.lower()
        
        # Check for sensitive indicators
        sensitive_indicators = [
            "password", "secret", "token", "credential", "api_key",
            "credit card", "ssn", "social security", "bank account",
            "personal information", "private key", "ssh key"
        ]
        
        for indicator in sensitive_indicators:
            if indicator in data_lower or indicator in context_lower:
                return "confidential"  # or "restricted" for highly sensitive
        
        # Check for internal indicators
        internal_indicators = [
            "internal", "company", "employee", "proprietary", "confidential"
        ]
        
        for indicator in internal_indicators:
            if indicator in data_lower or indicator in context_lower:
                return "internal"
        
        # Default to public
        return "public"
    
    def check_compliance(self, user_id: str, action: str, resource: str) -> Dict[str, Any]:
        """
        Check if an action complies with governance policies
        
        Args:
            user_id: User performing action
            action: Action being performed
            resource: Resource being accessed
            
        Returns:
            Compliance check results
        """
        result = {
            "compliant": True,
            "violations": [],
            "requires_review": False,
            "access_approved": True
        }
        
        # Check access control policies
        access_result = self.validate_access_request(user_id, resource, action)
        if not access_result["authorized"]:
            result["compliant"] = False
            result["violations"].append("Access unauthorized")
        
        # Check data handling based on classification
        classification = self.classify_data(resource, f"user {user_id} accessing via {action}")
        if classification in ["confidential", "restricted"]:
            # Additional checks for sensitive data
            if not access_result.get("requires_mfa", False):
                result["requires_review"] = True
                result["violations"].append(f"Additional review required for {classification} data")
        
        # Log compliance check
        self._log_compliance_event("compliance_check", {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "classification": classification,
            "result": result
        })
        
        return result
    
    def _log_compliance_event(self, event_type: str, details: Dict[str, Any]):
        """
        Log a compliance event
        
        Args:
            event_type: Type of event
            details: Event details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        # Load existing log or create new
        if self.compliance_log.exists():
            with open(self.compliance_log, "r") as f:
                log = json.load(f)
        else:
            log = []
        
        # Add new entry
        log.append(log_entry)
        
        # Limit log size to prevent it from growing indefinitely
        max_log_entries = 1000
        if len(log) > max_log_entries:
            log = log[-max_log_entries:]  # Keep only last N entries
        
        # Write back to file
        with open(self.compliance_log, "w") as f:
            json.dump(log, f, indent=2)
    
    def get_compliance_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get compliance log entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of log entries
        """
        if not self.compliance_log.exists():
            return []
        
        with open(self.compliance_log, "r") as f:
            log = json.load(f)
        
        # Return last N entries
        return log[-limit:]
    
    def generate_compliance_report(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Generate a compliance report
        
        Args:
            start_date: Starting date for report (ISO format)
            end_date: Ending date for report (ISO format)
            
        Returns:
            Compliance report
        """
        all_events = self.get_compliance_log(limit=10000)  # Get more entries for report
        
        # Filter by date if specified
        if start_date or end_date:
            filtered_events = []
            start_dt = datetime.fromisoformat(start_date) if start_date else datetime.min
            end_dt = datetime.fromisoformat(end_date) if end_date else datetime.max
            
            for event in all_events:
                event_dt = datetime.fromisoformat(event["timestamp"])
                if start_dt <= event_dt <= end_dt:
                    filtered_events.append(event)
            all_events = filtered_events
        
        # Generate statistics
        event_counts = {}
        violations_count = 0
        
        for event in all_events:
            event_type = event["event_type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # Count violations
            if "details" in event and "violations" in event["details"]:
                if event["details"]["violations"]:
                    violations_count += 1
        
        report = {
            "report_generated": datetime.now().isoformat(),
            "period_start": start_date or "beginning",
            "period_end": end_date or "now",
            "total_events": len(all_events),
            "event_types": event_counts,
            "total_violations": violations_count,
            "violation_details": []
        }
        
        # Add details of violations
        for event in all_events:
            if ("details" in event and 
                "violations" in event["details"] and 
                event["details"]["violations"]):
                report["violation_details"].append({
                    "timestamp": event["timestamp"],
                    "type": event["event_type"],
                    "details": event["details"]
                })
        
        return report
    
    def is_privilege_escalation(self, user_id: str, requested_role: str) -> bool:
        """
        Check if a role request constitutes privilege escalation
        
        Args:
            user_id: User requesting role
            requested_role: Role being requested
            
        Returns:
            True if this is privilege escalation
        """
        # This would normally check against current user roles vs. requested role
        # For demo, we'll say any role request other than "user" is escalation
        return requested_role.lower() not in ["user", "read_only"]
    
    def requires_approval(self, action: str, classification: str) -> bool:
        """
        Determine if an action requires approval based on governance policies
        
        Args:
            action: Action being performed
            classification: Data/resource classification level
            
        Returns:
            True if approval is required
        """
        policy = self.get_policy("authorization")
        
        # Actions that typically require approval
        approval_required_actions = ["delete", "modify_system", "access_restricted_data"]
        high_classification_levels = ["confidential", "restricted"]
        
        if action in approval_required_actions:
            return True
        
        if classification in high_classification_levels:
            return True
        
        return False


# Global instance for convenience
governance_policy = GovernancePolicy()


def get_governance_policy() -> GovernancePolicy:
    """
    Get governance policy instance
    
    Returns:
        GovernancePolicy instance
    """
    global governance_policy
    return governance_policy