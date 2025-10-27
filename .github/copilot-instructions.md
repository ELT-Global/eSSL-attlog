# Copilot Instructions for eSSL-attlog

## Project Overview

This repository contains **eSSL-attlog**, an attendance logging system built on top of PyZk and reverse-engineered eSSL push APIs. The project is written in Python and focuses on interfacing with eSSL biometric attendance devices to collect and process attendance data.

### Purpose
- Interface with eSSL biometric attendance devices
- Leverage PyZk library for device communication
- Process and log attendance records
- Utilize reverse-engineered eSSL push APIs for data synchronization

## Contribution Guidelines

### Development Environment
- **Language**: Python 3.x
- **Key Dependencies**: PyZk (for eSSL device communication)
- Follow PEP 8 style guidelines for Python code
- Use descriptive variable and function names

### Code Quality
- Write clear, maintainable Python code
- Add docstrings to all functions and classes following Google or NumPy style
- Include type hints where appropriate (Python 3.5+)
- Handle exceptions appropriately with informative error messages

### Testing
- Write unit tests for new functionality when possible
- Test device communication features carefully
- Include integration tests for API endpoints
- Verify attendance data processing logic

### Version Control
- Write clear, descriptive commit messages
- Keep commits focused on single logical changes
- Reference related issues in commit messages when applicable

## Project Structure

```
eSSL-attlog/
├── .github/              # GitHub configuration files
│   └── copilot-instructions.md
├── .gitignore           # Python-specific gitignore
├── LICENSE              # Project license
└── README.md            # Project documentation
```

### Expected Future Structure
As the project grows, the following structure is anticipated:
- `/src` or root-level `.py` files - Main source code
- `/tests` - Test files
- `/docs` - Additional documentation
- `/examples` - Usage examples
- `requirements.txt` or `pyproject.toml` - Python dependencies
- `setup.py` or `pyproject.toml` - Package configuration

## Technical Principles

### Python Best Practices
- Follow PEP 8 style guide
- Use virtual environments for dependency management
- Prefer composition over inheritance
- Keep functions small and focused (single responsibility)
- Use context managers for resource management (files, connections)

### Device Communication
- Handle network timeouts gracefully
- Implement retry logic for device communication
- Log all device interactions for debugging
- Validate device responses before processing

### Data Processing
- Validate attendance data integrity
- Handle timezone conversions correctly
- Ensure data privacy and security
- Implement proper error handling for API calls

### Security Considerations
- Never commit device credentials or API keys
- Use environment variables for sensitive configuration
- Validate and sanitize all input data
- Follow secure coding practices for API implementations

## Copilot Coding Agent Guidance

### Primary Focus Areas
- Python source files for attendance logging functionality
- Device communication modules using PyZk
- API integration for eSSL push services
- Data processing and validation logic

### Files to Approach with Care
- Configuration files containing device credentials
- Any reverse-engineered API implementation (document thoroughly)
- Network communication code (ensure proper error handling)

### Testing Requirements
- Test device communication with mock objects when possible
- Include edge cases for attendance data processing
- Verify timezone handling and data formatting
- Test error conditions and recovery mechanisms

### Documentation
- Document all reverse-engineered API endpoints
- Include examples for device configuration
- Explain attendance data formats and schemas
- Provide troubleshooting guidelines for common issues

### Code Review Checklist
- [ ] PEP 8 compliance
- [ ] Proper error handling and logging
- [ ] Security considerations addressed
- [ ] Tests included for new functionality
- [ ] Documentation updated
- [ ] No hardcoded credentials or sensitive data
- [ ] Type hints added where appropriate
- [ ] Docstrings following consistent style

## Dependencies and Setup

### Expected Python Dependencies
- PyZk - For eSSL device communication
- Standard library modules for data processing
- Additional dependencies as the project evolves

### Development Setup
When adding setup instructions:
1. Create and activate a virtual environment
2. Install dependencies from `requirements.txt` or `pyproject.toml`
3. Configure device connection parameters
4. Run tests to verify setup

## Working with Issues

### Issue Formatting for Copilot
When creating or working on issues:
- Provide clear acceptance criteria
- Include specific examples of expected behavior
- Reference related device models or API versions
- Specify test scenarios if applicable
- Tag with appropriate labels (bug, enhancement, documentation, etc.)

### Good Issue Example
```
Title: Add support for TK-100 device model

Description:
Add support for the eSSL TK-100 biometric device model.

Acceptance Criteria:
- Device connection established using PyZk
- Attendance records retrieved successfully
- Data format matches existing schema
- Include unit tests for TK-100 specific features

Test Scenarios:
- Connect to TK-100 device
- Retrieve attendance logs for the last 24 hours
- Handle device disconnection gracefully
```

## Additional Notes

### Project Status
This is an early-stage project. The codebase will evolve as features are added. Follow the principles above to maintain consistency as the project grows.

### Community
- Be respectful and constructive in all interactions
- Welcome contributions from the community
- Provide helpful feedback on pull requests
- Share knowledge about eSSL devices and attendance systems

### Resources
- PyZk Documentation: [fananimi/pyzk on GitHub](https://github.com/fananimi/pyzk) - Python library for ZKTeco attendance devices
- eSSL Device Documentation: Contact eSSL manufacturer for device-specific API documentation and specifications, or refer to device manuals
- Python Best Practices: [PEP 8](https://peps.python.org/pep-0008/), [PEP 257](https://peps.python.org/pep-0257/), and other relevant PEPs
- Attendance Device Resources: Community forums and reverse-engineering documentation for attendance systems
