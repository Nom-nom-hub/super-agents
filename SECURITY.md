# Security Policy

## Security Improvements

This document outlines the security improvements made to address vulnerabilities identified by static analysis tools.

### Fixed Vulnerabilities

1. **Command Injection (High Severity)**
   - **Issue**: Use of `os.system()` with potentially untrusted input
   - **Location**: `super_agents/cli/main.py`
   - **Fix**: Replaced `os.system()` with `subprocess.run()` using shell=False and argument lists
   - **Details**: 
     - Fixed script execution vulnerability (line ~293)
     - Fixed dependency installation vulnerability (line ~570)

2. **Hardcoded Temp Directory (Medium Severity)**
   - **Issue**: Use of hardcoded `/tmp` directory
   - **Location**: `super_agents/core/delegation_prompt_generator.py`
   - **Fix**: Used `tempfile.TemporaryDirectory()` context manager
   - **Details**: Ensures secure, unique temporary directory creation

### Security Best Practices

- Always use `subprocess.run()` with `shell=False` and argument lists instead of `os.system()`
- Validate and sanitize file paths before execution
- Use secure temporary directory creation instead of hardcoded paths
- Minimize use of shell execution for external commands

### Ongoing Security

- Regular security scanning with tools like Bandit
- Code review process includes security checks
- Dependency updates to address known vulnerabilities