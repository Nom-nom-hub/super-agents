#!/usr/bin/env python3
"""
Security configuration and governance for super-agents system
Implements security measures for sensitive information handling
"""

import base64
import configparser
import hashlib
import hmac
import os
import secrets
from pathlib import Path
from typing import Dict, Optional


class SecurityConfig:
    """
    Security configuration and governance for super-agents system

    Handles:
    - API key and credential management
    - Sensitive data protection
    - Access controls
    - Audit logging
    - Encryption utilities
    """

    def __init__(self, config_dir: str = None):
        """
        Initialize security configuration

        Args:
            config_dir: Directory for security configuration files
        """
        if config_dir is None:
            config_dir = os.path.join(os.getcwd(), "config")

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Security settings
        self.security_file = self.config_dir / "security.ini"
        self.api_keys_file = self.config_dir / "api_keys.ini"
        self.audit_log_file = self.config_dir / "audit.log"

        # Initialize default security settings
        self._initialize_security_config()

    def _initialize_security_config(self):
        """Initialize security configuration with defaults"""
        if not self.security_file.exists():
            config = configparser.ConfigParser()

            # Default security settings
            config["DEFAULT"] = {}
            config["API_KEYS"] = {}
            config["ENCRYPTION"] = {
                "enabled": "true",
                "algorithm": "sha256",
                "key_rotation_days": "30",
            }
            config["ACCESS_CONTROL"] = {
                "max_login_attempts": "3",
                "lockout_duration_minutes": "15",
                "session_timeout_minutes": "60",
            }
            config["AUDIT"] = {
                "enabled": "true",
                "log_sensitive_operations": "true",
                "retention_days": "90",
            }

            # Write the config file
            with open(self.security_file, "w") as f:
                config.write(f)

    def hash_secret(self, secret: str, salt: Optional[str] = None) -> tuple:
        """
        Hash a secret value safely

        Args:
            secret: Value to hash
            salt: Optional salt (generated if not provided)

        Returns:
            Tuple of (hashed_secret, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)

        # Use HMAC with SHA256 for hashing
        hashed = hmac.new(
            salt.encode("utf-8"), secret.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return hashed, salt

    def verify_hash(self, secret: str, hashed: str, salt: str) -> bool:
        """
        Verify a hashed secret

        Args:
            secret: Original secret
            hashed: Hashed value to verify against
            salt: Salt used for original hashing

        Returns:
            True if verification succeeds
        """
        computed_hash, _ = self.hash_secret(secret, salt)
        return hmac.compare_digest(computed_hash, hashed)

    def store_api_key(self, service: str, api_key: str) -> bool:
        """
        Securely store an API key

        Args:
            service: Service name
            api_key: API key value

        Returns:
            True if storage succeeds
        """
        try:
            # Hash the API key before storing
            hashed_key, salt = self.hash_secret(api_key)

            # Load existing config or create new one
            config = configparser.ConfigParser()
            if self.api_keys_file.exists():
                config.read(self.api_keys_file)

            # Add to config
            if "API_KEYS" not in config:
                config["API_KEYS"] = {}

            # Store both the hash and salt
            config["API_KEYS"][f"{service}_hash"] = hashed_key
            config["API_KEYS"][f"{service}_salt"] = salt

            # Write to file
            with open(self.api_keys_file, "w") as f:
                config.write(f)

            return True
        except Exception as e:
            print(f"Error storing API key: {e}")
            return False

    def retrieve_api_key(self, service: str) -> Optional[str]:
        """
        Retrieve stored API key (not recommended in production -
        this is a demo implementation)

        Args:
            service: Service name

        Returns:
            API key if found and verified
        """
        # NOTE: This is only for demonstration. In production, you would not
        # return the actual API key, but rather use it internally.
        try:
            config = configparser.ConfigParser()
            if not self.api_keys_file.exists():
                return None

            config.read(self.api_keys_file)

            hash_key = config.get("API_KEYS", f"{service}_hash", fallback=None)
            salt = config.get("API_KEYS", f"{service}_salt", fallback=None)

            if not hash_key or not salt:
                return None

            # In a real implementation, you'd use this to verify some input
            # rather than returning the original value
            return f"<{service}_api_key_hashed>"

        except Exception as e:
            print(f"Error retrieving API key: {e}")
            return None

    def validate_api_key(self, service: str, provided_key: str) -> bool:
        """
        Validate an API key against stored hash

        Args:
            service: Service name
            provided_key: Provided key to validate

        Returns:
            True if validation succeeds
        """
        try:
            config = configparser.ConfigParser()
            if not self.api_keys_file.exists():
                return False

            config.read(self.api_keys_file)

            stored_hash = config.get("API_KEYS", f"{service}_hash", fallback=None)
            salt = config.get("API_KEYS", f"{service}_salt", fallback=None)

            if not stored_hash or not salt:
                return False

            return self.verify_hash(provided_key, stored_hash, salt)

        except Exception:
            return False

    def sanitize_input(self, data: str) -> str:
        """
        Sanitize input to prevent injection attacks

        Args:
            data: Input string to sanitize

        Returns:
            Sanitized string
        """
        # Remove potentially dangerous characters/sequences
        dangerous_patterns = [
            "../",  # Directory traversal
            "<script",  # XSS attempts
            "eval(",  # Code execution
            "exec(",  # Code execution
            "import ",  # Module import
        ]

        sanitized = data
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, "[FILTERED]")

        return sanitized

    def is_safe_path(self, path: str, allowed_base: str = None) -> bool:
        """
        Check if a path is safe to access (prevent directory traversal)

        Args:
            path: Path to check
            allowed_base: Base directory that access is allowed in

        Returns:
            True if path is safe
        """
        if allowed_base is None:
            allowed_base = str(self.config_dir.parent.absolute())

        try:
            # Resolve to absolute path to check for traversal
            abs_path = (Path(allowed_base) / path).resolve()
            base_path = Path(allowed_base).resolve()

            # Check if resolved path is within allowed base
            abs_path.relative_to(base_path)
            return True
        except ValueError:
            # If relative_to raises ValueError, path is outside base
            return False

    def log_audit_event(
        self,
        event_type: str,
        user: str,
        action: str,
        resource: str = None,
        success: bool = True,
        details: Dict = None,
    ) -> bool:
        """
        Log an audit event

        Args:
            event_type: Type of event (login, access, modification, etc.)
            user: User performing action
            action: Action performed
            resource: Resource affected
            success: Whether action succeeded
            details: Additional details

        Returns:
            True if logging succeeds
        """
        try:
            audit_entry = (
                f"[{event_type.upper()}] "
                f"USER={user} "
                f"ACTION={action} "
                f"RESOURCE={resource or 'N/A'} "
                f"SUCCESS={success} "
                f"TIMESTAMP={os.times().elapsed} "
            )

            if details:
                audit_entry += f"DETAILS={str(details)} "

            audit_entry += "\n"

            with open(self.audit_log_file, "a") as f:
                f.write(audit_entry)

            return True
        except Exception as e:
            print(f"Error logging audit event: {e}")
            return False

    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate a cryptographically secure token

        Args:
            length: Length of token in bytes

        Returns:
            Hex-encoded secure token
        """
        return secrets.token_hex(length)

    def check_password_strength(self, password: str) -> Dict[str, bool]:
        """
        Check strength of a password

        Args:
            password: Password to check

        Returns:
            Dict with strength indicators
        """
        checks = {
            "length": len(password) >= 12,
            "uppercase": any(c.isupper() for c in password),
            "lowercase": any(c.islower() for c in password),
            "digit": any(c.isdigit() for c in password),
            "special_char": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password),
            "no_common_patterns": not any(
                pattern in password.lower()
                for pattern in ["password", "123456", "qwerty", "admin"]
            ),
        }
        return checks

    def encrypt_data(self, data: str, key: Optional[str] = None) -> str:
        """
        Encrypt data using Fernet (needs cryptography package)
        This is a placeholder that returns masked data if cryptography isn't available

        Args:
            data: Data to encrypt
            key: Encryption key (generates if not provided)

        Returns:
            Encrypted data
        """
        try:
            from cryptography.fernet import Fernet

            if key is None:
                key = Fernet.generate_key()
            elif isinstance(key, str):
                # If key is provided as string, encode it
                if len(key) != 44 or not key.endswith("="):  # Basic Fernet key check
                    # Convert string to proper Fernet key
                    key = base64.urlsafe_b64encode(
                        hashlib.sha256(key.encode()).digest()
                    )

            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data.encode())
            return encrypted_data.decode()
        except ImportError:
            # Fallback: just mask the data
            print("Warning: 'cryptography' package not found. Using basic masking.")
            return f"ENCRYPTED:{hashlib.sha256(data.encode()).hexdigest()[:16]}..."

    def decrypt_data(self, encrypted_data: str, key: str) -> str:
        """
        Decrypt data using Fernet
        Placeholder implementation

        Args:
            encrypted_data: Data to decrypt
            key: Decryption key

        Returns:
            Decrypted data
        """
        try:
            from cryptography.fernet import Fernet

            if isinstance(key, str) and len(key) != 44:  # Not a proper Fernet key
                # Convert string to proper Fernet key
                key = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())

            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except ImportError:
            # Since encryption was just masking, return a notification
            return "[DECRIPTION_NOT_AVAILABLE: cryptography package required]"


# Global instance for convenience
security_config = SecurityConfig()


def get_security_config() -> SecurityConfig:
    """
    Get security configuration instance

    Returns:
        SecurityConfig instance
    """
    global security_config
    return security_config
