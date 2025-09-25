# Security Policy

## Supported Versions

This section outlines the security support status for different versions of PDF Duplicate Finder.

| Version | Supported | Security Updates |
|---------|-----------|------------------|
| 3.0.x   | ✅ Yes    | Yes              |
| 2.12.x  | ⚠️ Limited | Critical only    |
| 2.11.x  | ❌ No     | No               |
| < 2.11  | ❌ No     | No               |

**Note**: Only the latest major version (3.0.x) receives full security support. Version 2.12.x may receive critical security updates on a case-by-case basis.

## Reporting a Vulnerability

### How to Report

If you discover a security vulnerability in PDF Duplicate Finder, please report it responsibly by following these steps:

1. **Email the Maintainer**
   - Send your report to: [nsfr750@yandex.com](mailto:nsfr750@yandex.com)
   - Use the subject line: **"Security Vulnerability Report - PDF Duplicate Finder"**

2. **Include the Following Information**
   - A clear description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact of the vulnerability
   - Your suggested mitigation (if any)
   - Your name and contact information (for follow-up questions)

3. **What to Expect**
   - Initial acknowledgment within 48 hours
   - Regular updates on the remediation progress
   - Coordinated disclosure timeline
   - Public disclosure after fix is released

### Responsible Disclosure

We follow responsible disclosure practices:

- **Initial Response**: We'll acknowledge receipt of your report within 48 hours
- **Assessment**: We'll assess the vulnerability severity and impact
- **Remediation**: We'll work on a fix and coordinate a release timeline
- **Disclosure**: We'll publicly disclose the vulnerability after a fix is available
- **Credit**: We'll credit you in the security advisory (with your permission)

### Do Not

- Do not create public issues about security vulnerabilities
- Do not disclose vulnerability details publicly before we've fixed the issue
- Do not use automated scanners that could disrupt the service
- Do not attempt to access or modify data you don't own

## Security Scope

### In Scope

The following security aspects are within the scope of this security policy:

- **File Processing Vulnerabilities**
  - PDF parsing and processing security issues
  - File path traversal vulnerabilities
  - Memory corruption during file operations
  - Buffer overflow vulnerabilities

- **Application Security**
  - Authentication and authorization bypasses
  - Input validation vulnerabilities
  - Cross-site scripting (XSS) in web interfaces (if any)
  - SQL injection (if database features are added)
  - Code injection vulnerabilities

- **Data Security**
  - Sensitive data exposure
  - Insecure data storage
  - Insecure data transmission
  - Information disclosure vulnerabilities

- **System Security**
  - Privilege escalation vulnerabilities
  - Denial of service (DoS) vulnerabilities
  - Race conditions
  - Insecure file permissions

### Out of Scope

The following are considered out of scope for this security policy:

- **Third-party Dependencies**
  - Vulnerabilities in PyQt6, PyMuPDF, or other dependencies
  - Issues in Ghostscript or Tesseract installations
  - Operating system level vulnerabilities

- **User Configuration**
  - Misconfigured user permissions
  - Weak user passwords
  - Insecure system configurations

- **Physical Security**
  - Physical access to the system
  - Hardware-level vulnerabilities
  - Network infrastructure issues

- **Social Engineering**
  - Phishing attacks
  - User education issues
  - Social engineering attempts

## Security Best Practices

### For Users

1. **File Handling**
   - Only process PDF files from trusted sources
   - Keep your PDF reader software updated
   - Be cautious with PDFs from unknown sources

2. **System Security**
   - Keep your operating system and antivirus software updated
   - Use strong passwords for your user account
   - Regular backup your important files

3. **Application Usage**
   - Download PDF Duplicate Finder only from official sources
   - Keep the application updated to the latest version
   - Report any suspicious behavior to the maintainers

### For Developers

1. **Code Security**
   - Follow secure coding practices
   - Validate all user inputs
   - Use safe file handling methods
   - Implement proper error handling

2. **Dependency Management**
   - Keep all dependencies updated
   - Regularly check for security advisories
   - Use dependency scanning tools
   - Review third-party code before inclusion

3. **Testing**
   - Include security testing in the development process
   - Perform code reviews with security focus
   - Use static analysis tools
   - Test with malformed or malicious files

## Vulnerability Response Process

### Severity Levels

We use the following severity levels for security vulnerabilities:

| Level | Description | Response Time |
|-------|-------------|---------------|
| **Critical** | High risk of system compromise, data loss, or service disruption | 24-48 hours |
| **High** | Significant security impact with potential for data exposure | 3-7 days |
| **Medium** | Moderate security impact with limited exploitation potential | 1-2 weeks |
| **Low** | Minor security issues with minimal impact | 1 month |

### Response Timeline

1. **Acknowledgment** (within 48 hours)
   - Confirm receipt of the vulnerability report
   - Assign severity level
   - Provide initial assessment timeline

2. **Investigation** (1-7 days)
   - Reproduce and validate the vulnerability
   - Assess the impact and scope
   - Develop remediation plan

3. **Remediation** (varies by severity)
   - Develop and test the fix
   - Prepare security advisory
   - Coordinate release timeline

4. **Disclosure** (after fix release)
   - Publish security advisory
   - Update affected versions
   - Credit the reporter (with permission)

## Security Advisories

Security advisories will be published on our [GitHub Security Advisories](https://github.com/Nsfr750/PDF_finder/security/advisories) page and will include:

- Vulnerability description and impact
- Affected versions
- Patched versions
- Mitigation steps
- Credit to the reporter (with permission)

## Contact Information

For security-related inquiries:

- **Security Reports**: [nsfr750@yandex.com](mailto:nsfr750@yandex.com)
- **GitHub Security**: [GitHub Security Advisories](https://github.com/Nsfr750/PDF_finder/security/advisories)
- **Discord**: [Join our Discord community](https://discord.gg/ryqNeuRYjD) for general discussions

## Legal Disclaimer

This security policy is provided "as is" without warranty of any kind. We reserve the right to modify this policy at any time without notice. While we strive to address all security vulnerabilities promptly, we cannot guarantee specific response times or outcomes.

---

*Last Updated: September 2025*
