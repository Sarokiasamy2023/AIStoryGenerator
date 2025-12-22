# 🚀 Production Deployment Guide

**Duration:** 1 day  
**Goal:** Deploy to production  
**Audience:** DevOps, Technical Leads, System Administrators

---

## 📋 Deployment Overview

This guide covers the complete production deployment process including infrastructure setup, configuration, security, monitoring, and rollout strategy.

---

## 🎯 Deployment Phases

### Phase 1: Pre-Deployment (2 hours)
- Infrastructure setup
- Security configuration
- Environment preparation

### Phase 2: Installation (2 hours)
- Software installation
- Dependency management
- Configuration

### Phase 3: Integration (2 hours)
- CI/CD integration
- Test migration
- Validation

### Phase 4: Rollout (2 hours)
- Gradual rollout
- Monitoring
- Team enablement

---

## Phase 1: Pre-Deployment (2 hours)

### Infrastructure Requirements

**Server Specifications:**
```
CPU: 4+ cores
RAM: 8GB minimum, 16GB recommended
Storage: 50GB minimum
OS: Windows Server 2019+ or Linux (Ubuntu 20.04+)
Network: Stable internet connection
```

**Software Requirements:**
```
Python: 3.8 or higher
Node.js: 14+ (optional, for development)
Git: Latest version
Browser: Chromium/Firefox/WebKit support
```

### Security Setup

#### 1. API Key Management

**Option A: Environment Variables (Recommended)**
```bash
# Windows
setx GEMINI_API_KEY "your_api_key_here" /M

# Linux
export GEMINI_API_KEY="your_api_key_here"
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
```

**Option B: Secrets Manager**
```python
# Use AWS Secrets Manager, Azure Key Vault, etc.
import boto3

def get_api_key():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='gemini-api-key')
    return response['SecretString']
```

#### 2. Network Security

```yaml
# Firewall rules
Inbound:
  - Port 8888: Dashboard access (internal only)
  - Port 443: HTTPS (if using SSL)

Outbound:
  - Port 443: Gemini API access
  - Port 443: Salesforce access
```

#### 3. Access Control

```python
# Add authentication to server
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "secure_password":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials
```

---

## Phase 2: Installation (2 hours)

### Step 1: Clone Repository

```bash
# Production server
cd /opt/automation  # Linux
# or
cd C:\Automation  # Windows

git clone <repository_url>
cd SalesforceAutomationRecorder
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_ai.txt

# Install Playwright browsers
playwright install chromium
```

### Step 3: Configuration

**config.json (Production)**
```json
{
  "browser": {
    "headless": true,
    "slowMo": 50,
    "viewport": {
      "width": 1920,
      "height": 1080
    }
  },
  "recording": {
    "captureScreenshots": true,
    "autoSave": true,
    "outputDirectory": "/var/automation/recordings"
  },
  "selectors": {
    "preferredStrategy": "css",
    "generateMultiple": true,
    "includeXPath": true
  }
}
```

**gemini_config.json (Production)**
```json
{
  "gemini_ai": {
    "enabled": true,
    "model": "gemini-pro",
    "max_retries": 3,
    "timeout_seconds": 30,
    "cache_enabled": true,
    "cache_ttl_hours": 24
  },
  "selector_strategies": {
    "use_traditional_first": true,
    "traditional_timeout_ms": 2000,
    "max_traditional_attempts": 10,
    "max_ai_suggestions": 15
  },
  "performance": {
    "track_metrics": true,
    "save_screenshots_on_failure": true,
    "debug_mode": false,
    "verbose_logging": false
  },
  "api_limits": {
    "max_requests_per_minute": 60,
    "enable_rate_limiting": true
  }
}
```

### Step 4: Service Setup

**Linux (systemd)**
```ini
# /etc/systemd/system/automation-server.service
[Unit]
Description=Automation Test Server
After=network.target

[Service]
Type=simple
User=automation
WorkingDirectory=/opt/automation/SalesforceAutomationRecorder
Environment="GEMINI_API_KEY=your_key_here"
ExecStart=/opt/automation/SalesforceAutomationRecorder/venv/bin/python ui_real_test_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable automation-server
sudo systemctl start automation-server
sudo systemctl status automation-server
```

**Windows (NSSM)**
```powershell
# Install NSSM
choco install nssm

# Create service
nssm install AutomationServer "C:\Automation\SalesforceAutomationRecorder\venv\Scripts\python.exe"
nssm set AutomationServer AppDirectory "C:\Automation\SalesforceAutomationRecorder"
nssm set AutomationServer AppParameters "ui_real_test_server.py"
nssm set AutomationServer AppEnvironmentExtra "GEMINI_API_KEY=your_key_here"

# Start service
nssm start AutomationServer
```

---

## Phase 3: Integration (2 hours)

### CI/CD Integration

#### Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        GEMINI_API_KEY = credentials('gemini-api-key')
        AUTOMATION_SERVER = 'http://automation-server:8888'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    // Run tests via API
                    def response = httpRequest(
                        url: "${AUTOMATION_SERVER}/api/run-test",
                        httpMode: 'POST',
                        contentType: 'APPLICATION_JSON',
                        requestBody: readFile('tests/smoke_test.json')
                    )
                    
                    if (response.status != 200) {
                        error("Tests failed")
                    }
                }
            }
        }
        
        stage('Publish Results') {
            steps {
                publishHTML([
                    reportDir: 'test_results',
                    reportFiles: 'index.html',
                    reportName: 'Test Report'
                ])
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'test_results/**/*', allowEmptyArchive: true
        }
    }
}
```

#### GitHub Actions

```yaml
# .github/workflows/automation-tests.yml
name: Automation Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run tests
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python run_production_tests.py
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test_results/
```

### Test Migration

**Convert existing tests:**
```python
# migrate_tests.py
import json
from pathlib import Path

def convert_selenium_to_framework(selenium_test):
    """Convert Selenium test to framework format"""
    steps = []
    
    for action in selenium_test['actions']:
        if action['type'] == 'sendKeys':
            steps.append(f'Type "{action["value"]}" into "{action["target"]}"')
        elif action['type'] == 'click':
            steps.append(f'Click "{action["target"]}"')
        elif action['type'] == 'select':
            steps.append(f'Select "{action["value"]}" from Dropdown "{action["target"]}"')
    
    return '\n'.join(steps)

# Migrate all tests
for test_file in Path('old_tests').glob('*.json'):
    with open(test_file) as f:
        old_test = json.load(f)
    
    new_test = convert_selenium_to_framework(old_test)
    
    output_file = Path('new_tests') / test_file.name.replace('.json', '.txt')
    output_file.write_text(new_test)
```

---

## Phase 4: Rollout (2 hours)

### Gradual Rollout Strategy

**Week 1: Pilot (10% of tests)**
```python
# Select stable, well-understood tests
pilot_tests = [
    'login_test.txt',
    'navigation_test.txt',
    'search_test.txt'
]

# Run daily
# Monitor metrics
# Gather feedback
```

**Week 2-3: Expansion (50% of tests)**
```python
# Add more complex tests
expansion_tests = pilot_tests + [
    'form_submission_test.txt',
    'data_validation_test.txt',
    'workflow_test.txt'
]

# Run twice daily
# Compare with old framework
# Optimize based on learnings
```

**Week 4: Full Rollout (100% of tests)**
```python
# Migrate all tests
# Decommission old framework
# Full production use
```

### Monitoring Setup

**Prometheus Metrics**
```python
# Add to ui_real_test_server.py
from prometheus_client import Counter, Histogram, start_http_server

test_executions = Counter('test_executions_total', 'Total test executions')
test_duration = Histogram('test_duration_seconds', 'Test execution duration')
ai_usage = Counter('ai_usage_total', 'Total AI consultations')

# Start metrics server
start_http_server(9090)
```

**Grafana Dashboard**
```json
{
  "dashboard": {
    "title": "Automation Metrics",
    "panels": [
      {
        "title": "Test Execution Rate",
        "targets": [{"expr": "rate(test_executions_total[5m])"}]
      },
      {
        "title": "Average Test Duration",
        "targets": [{"expr": "avg(test_duration_seconds)"}]
      },
      {
        "title": "AI Usage",
        "targets": [{"expr": "rate(ai_usage_total[1h])"}]
      }
    ]
  }
}
```

### Logging Setup

**Centralized Logging**
```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger('automation')
    logger.setLevel(logging.INFO)
    
    # File handler
    handler = RotatingFileHandler(
        'logs/automation.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

---

## 📊 Production Checklist

### Pre-Deployment
- [ ] Infrastructure provisioned
- [ ] Security configured
- [ ] API keys secured
- [ ] Network access verified
- [ ] Backup strategy defined

### Installation
- [ ] Software installed
- [ ] Dependencies verified
- [ ] Configuration updated
- [ ] Service configured
- [ ] Health check passing

### Integration
- [ ] CI/CD pipeline configured
- [ ] Tests migrated
- [ ] Validation complete
- [ ] Documentation updated
- [ ] Team trained

### Rollout
- [ ] Pilot successful
- [ ] Metrics baseline established
- [ ] Monitoring active
- [ ] Alerts configured
- [ ] Rollback plan ready

---

## 🔧 Maintenance

### Daily Tasks
- Monitor dashboard for failures
- Review error logs
- Check AI usage metrics

### Weekly Tasks
- Review performance trends
- Optimize slow tests
- Update learned selectors if needed

### Monthly Tasks
- Review AI costs
- Update dependencies
- Performance tuning
- Team feedback session

---

## 📈 Success Metrics

Track these KPIs:

**Performance:**
- Test execution time
- Reuse efficiency
- AI usage percentage

**Reliability:**
- Success rate
- False failure rate
- Self-healing success rate

**Cost:**
- AI API costs
- Infrastructure costs
- Maintenance hours

**Adoption:**
- Tests migrated
- Team usage
- Feedback score

---

## 🆘 Support & Troubleshooting

### Common Issues

**Issue:** High AI usage costs
**Solution:** Increase traditional selector attempts, optimize learning

**Issue:** Slow test execution
**Solution:** Enable headless mode, optimize waits, use Enhanced mode

**Issue:** Service crashes
**Solution:** Check logs, increase memory, review error patterns

### Getting Help

1. Check logs: `/var/log/automation/`
2. Review metrics: Grafana dashboard
3. Check documentation: `COMPLETE_DOCUMENTATION.md`
4. Contact support team

---

## 🎯 Post-Deployment

### Week 1
- Daily monitoring
- Quick issue resolution
- Team support

### Month 1
- Performance review
- Cost analysis
- Optimization opportunities

### Quarter 1
- ROI calculation
- Expansion planning
- Feature requests

---

**Deployment complete! Monitor metrics and iterate based on feedback.**
