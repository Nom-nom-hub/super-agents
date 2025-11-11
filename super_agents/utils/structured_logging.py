#!/usr/bin/env python3
"""
Structured logging configuration for super-agents system
Implements consistent logging across all agent components
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import os


class StructuredLogger:
    """Provides structured logging for agent operations"""
    
    def __init__(self, name: str, log_dir: str = None, level: str = "INFO"):
        """
        Initialize structured logger
        
        Args:
            name: Name of the logger (usually agent id)
            log_dir: Directory to store logs (default: company/logs/)
            level: Logging level
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent adding handlers multiple times
        if not self.logger.handlers:
            # Create logs directory
            if log_dir is None:
                log_dir = os.path.join(os.getcwd(), "logs")
            
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)
            
            # Create structured JSON log file handler
            log_file = log_path / f"{name}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(StructuredFormatter())
            
            # Add file handler
            self.logger.addHandler(file_handler)
            
            # Also add console handler for dev/debug
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(console_handler)
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """Internal logging method"""
        extra_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "logger": self.name,
            **kwargs
        }
        
        getattr(self.logger, level.lower())(message, extra=extra_data)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info level message"""
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning level message"""
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error level message"""
        self._log("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug level message"""
        self._log("DEBUG", message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical level message"""
        self._log("CRITICAL", message, **kwargs)


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs"""
    
    def format(self, record) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": getattr(record, 'logger', 'unknown'),
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add any extra fields that were passed
        for key, value in record.__dict__.items():
            if key not in log_entry and not key.startswith('_'):
                log_entry[key] = value
        
        return json.dumps(log_entry)


def setup_logging_config(log_dir: str = None, level: str = "INFO") -> Dict[str, Any]:
    """
    Setup structured logging configuration for the entire system
    
    Args:
        log_dir: Directory to store logs
        level: Default logging level
        
    Returns:
        Logging configuration dictionary
    """
    if log_dir is None:
        log_dir = os.path.join(os.getcwd(), "logs")
    
    # Create directory if not exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": StructuredFormatter
            }
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "filename": os.path.join(log_dir, "super_agents.log"),
                "formatter": "structured",
                "mode": "a"
            },
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "structured"
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["file", "console"],
                "level": level.upper(),
                "propagate": False
            }
        }
    }
    
    return config


def get_logger(name: str, log_dir: str = None, level: str = "INFO") -> StructuredLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Name of the logger
        log_dir: Directory to store logs
        level: Logging level
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, log_dir, level)


def log_agent_execution(agent_id: str, task: str, status: str, duration: float = None, 
                       result: Dict[str, Any] = None, error: str = None,
                       log_dir: str = None) -> None:
    """
    Log an agent execution with structured format
    
    Args:
        agent_id: ID of the agent executing
        task: Description of the task
        status: Execution status (success, failed, partial, etc.)
        duration: Execution duration in seconds
        result: Result data from execution
        error: Error message if any
        log_dir: Directory to store logs
    """
    logger = get_logger("execution_tracker", log_dir)
    
    log_data = {
        "agent_id": agent_id,
        "task": task,
        "status": status,
    }
    
    if duration is not None:
        log_data["duration_seconds"] = duration
    
    if result is not None:
        log_data["result"] = result
    
    if error is not None:
        log_data["error"] = error
    
    logger.info(f"Agent execution completed: {status}", **log_data)


def log_agent_decision(agent_id: str, decision: str, rationale: str = None, 
                      options_considered: list = None, log_dir: str = None) -> None:
    """
    Log an agent decision with structured format
    
    Args:
        agent_id: ID of the agent making decision
        decision: The decision made
        rationale: Reasoning behind the decision
        options_considered: List of options that were considered
        log_dir: Directory to store logs
    """
    logger = get_logger("decision_logger", log_dir)
    
    log_data = {
        "agent_id": agent_id,
        "decision": decision,
    }
    
    if rationale is not None:
        log_data["rationale"] = rationale
    
    if options_considered is not None:
        log_data["options_considered"] = options_considered
    
    logger.info("Agent decision recorded", **log_data)


def log_agent_tool_usage(agent_id: str, tool_name: str, parameters: Dict[str, Any] = None,
                        result: str = None, duration: float = None, log_dir: str = None) -> None:
    """
    Log tool usage by an agent
    
    Args:
        agent_id: ID of the agent using the tool
        tool_name: Name of the tool
        parameters: Parameters passed to the tool
        result: Result of the tool execution
        duration: Execution time in seconds
        log_dir: Directory to store logs
    """
    logger = get_logger("tool_usage_logger", log_dir)
    
    log_data = {
        "agent_id": agent_id,
        "tool_name": tool_name,
    }
    
    if parameters is not None:
        log_data["parameters"] = parameters
    
    if result is not None:
        log_data["result"] = result
    
    if duration is not None:
        log_data["duration_seconds"] = duration
    
    logger.info("Agent tool usage", **log_data)


# Initialize a system logger at the module level
system_logger = get_logger("system")


def log_system_event(event_type: str, message: str, **kwargs) -> None:
    """
    Log a system-level event
    
    Args:
        event_type: Type of system event
        message: Event description
        **kwargs: Additional event data
    """
    system_logger.info(message, event_type=event_type, **kwargs)