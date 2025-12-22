# Fine-Tuning Guide for AI Test Generator

This guide shows you how to create a custom AI model trained specifically on your test cases and format.

---

## 🎯 Why Fine-Tune?

Fine-tuning creates a custom model that:
- ✅ Always generates in YOUR exact format
- ✅ Understands YOUR field names and workflows
- ✅ Produces consistent, detailed output (50-100+ steps)
- ✅ Doesn't need examples every time
- ✅ Learns YOUR organization's patterns

---

## 📋 Prerequisites

1. OpenAI API account with fine-tuning access
2. At least 10-50 example test cases in your format
3. Python installed (for OpenAI CLI)
4. Budget: ~$10-50 for training (one-time cost)

---

## 🔧 Step 1: Prepare Training Data

### **Create training-data.jsonl**

Each line is ONE complete example in JSONL format:

```jsonl
{"messages": [{"role": "system", "content": "You are a QA automation engineer generating detailed Salesforce test automation steps."}, {"role": "user", "content": "Generate detailed test steps for completing HSD Performance Report form HSD-01059 with all pages including login, navigation, form fields, and submission"}, {"role": "assistant", "content": "# Salesforce HSD Performance Reports - Complete Workflow Test\n \n# Login\nNavigate to https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/\nWait for 2 seconds\nType \"sarokiasamy2@dmigs.com.dcp.dcpuat\" into Username\nType \"Grantee@456\" into Password\nClick \"Log in\"\nWait for 2 seconds\n \n# Agreement Page\nClick \"I Disagree\"\nClick \"Next\"\nWait for 2 seconds\nClick \"Next\"\nClick \"Finish\"\nWait for 3 seconds\n \n# Navigate to HSD Performance Reports\nClick \"HSD PERFORMANCE REPORTS\"\nWait for 2 seconds\nClick \"Recently Viewed\"\nWait for 1 seconds\nClick \"In Progress Reports\"\nWait for 2 seconds\nClick \"HSD-01059\"\nWait for 1 seconds\n \n# Start/Edit Form\nClick \"Edit\"\nWait for 2 seconds\nClick \"Next\"\n \n# Complete Form - Page 1\nType \"5110\" into \"Number of people on listserv\"\nType \"0\" into \"Number of people receiving newsletter (via mail or electronic)\"\nType \"0\" into \"How many newsletter issues per year (if known)?\"\nType \"54\" into \"How many listserv posts distributed per year (if known)?\"\nType \"22016\" into \"Number of website hits- Specify most popular sections of websites (if known) - Value\"\nType \"The most popular sections were: (1) Hawaii State Office of Primary Care & Rural Health: Home Page, FQHC, HPSA, MUA/MUP; (2) Hawaii State Rural Health Association: Home Page, About, Programs, Membership; and (3) Project ECHO Hawaii: Home Page, Register, Behavioral Health ECHO Resources, What is ECHO?\" into \"Number of website hits- Specify most popular sections of websites (if known) - Specify(Allows 2000 characters)\"\nSelect \"No\" from \"Is the audience/membership for the listserv the same as for the newsletter?\"\nSelect \"Interactive\" from \"Is the listserv one-way information or interactive?\"\nSelect \"NA/None\" from \"Articles\"\nSelect \"Hosted or Co-Hosted\" from \"Conferences (hosted or co-hosted)\"\nSelect \"New\" from \"Fact Sheets\"\nSelect \"New\" from \"Maps\"\nSelect \"New\" from \"Newsletter\"\nSelect \"New\" from \"Toolkits\"\nSelect \"New\" from \"Webinars\"\nSelect \"New\" from \"Websites\"\nType \"The Hawaii State Office of Primary Care & Rural Health, in partnership with the Hawaii State Rural Health Association, has completed a Maui Together Wildfire Assessment.\" into \"Describe one tool that you created to address a problem in your state.\"\nClick \"Next\"\nWait for 1 seconds\n \n# Complete Form - Page 2\nSelect \"New\" from \"Behavioral Health\"\nSelect \"New\" from \"Community Development\"\nSelect \"New\" from \"Grant Writing\"\nSelect \"New\" from \"Needs Assesment\"\nSelect \"New\" from \"Older Adults/Aging\"\nSelect \"New\" from \"Opioids\"\nSelect \"New\" from \"Oral Health\"\nSelect \"New\" from \"Population health\"\nSelect \"New\" from \"Rural Health Network\"\nSelect \"New\" from \"Telehealth\"\nSelect \"New\" from \"Transportation\"\nSelect \"New\" from \"Tribals\"\nSelect \"New\" from \"Veterans\"\nSelect \"New\" from \"Workforce\"\nSelect \"New\" from \"Other\"\nType \"Sample comment\" into \"Other-Specify (Allows 2000 characters)\"\nCheck \"Critical Access Hospitals\" checkbox\nType \"Test\" into \"Collaborative effort in your state\"\nClick \"Next\"\nWait for 1 seconds\n \n# Complete Form - Page 3\nType \"107\" into \"Face to Face\"\nType \"Test\" into \"Face to Face description\"\nType \"49\" into \"Academic Institutions\"\nType \"Test\" into \"Academic Institutions Description\"\nClick \"Next\"\nWait for 1 seconds\n \n# Upload and Comments\nClick \"Upload\"\nType \"comment text\" into \"Comments\"\n \n# Submit for Approval\nClick \"Next\"\nWait for 1 seconds\nVerify \"Submit\" is visible\nClick \"Submit\"\nWait for 3 seconds\nVerify \"Form submitted successfully\""}]}
```

### **Helper Script to Create Training Data**

Create: `create-training-data.js`

```javascript
const fs = require('fs');

// Your examples
const examples = [
    {
        userRequest: "Generate detailed test steps for completing HSD Performance Report form HSD-01059 with all pages",
        assistantResponse: `# Salesforce HSD Performance Reports - Complete Workflow Test
 
# Login
Navigate to https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/
Wait for 2 seconds
Type "sarokiasamy2@dmigs.com.dcp.dcpuat" into Username
Type "Grantee@456" into Password
Click "Log in"
Wait for 2 seconds
[... rest of your complete test steps ...]`
    },
    {
        userRequest: "Generate test steps for CBD Form 1 Demographics with Counties Served, Full Patient Panel fields",
        assistantResponse: `# CBD Performance Reports - Form 1 Demographics
 
# Login
Navigate to https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/
Wait for 2 seconds
[... rest of your test steps ...]`
    }
    // Add 10-50 more examples
];

// Convert to JSONL format
const jsonl = examples.map(ex => JSON.stringify({
    messages: [
        {
            role: "system",
            content: "You are a QA automation engineer generating detailed Salesforce test automation steps."
        },
        {
            role: "user",
            content: ex.userRequest
        },
        {
            role: "assistant",
            content: ex.assistantResponse
        }
    ]
})).join('\n');

fs.writeFileSync('training-data.jsonl', jsonl);
console.log('✅ Training data created: training-data.jsonl');
console.log(`📊 Total examples: ${examples.length}`);
```

Run: `node create-training-data.js`

---

## 🚀 Step 2: Upload and Fine-Tune

### **Install OpenAI CLI**

```bash
pip install openai
```

### **Set API Key**

Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="sk-proj-your-api-key-here"
```

### **Upload Training File**

```bash
openai api fine_tuning.jobs.create -t training-data.jsonl -m gpt-4o-mini-2024-07-18
```

### **Check Status**

```bash
# List all fine-tuning jobs
openai api fine_tuning.jobs.list

# Get specific job status
openai api fine_tuning.jobs.retrieve -i ftjob-abc123
```

**Training takes 10-60 minutes** depending on data size.

---

## 📝 Step 3: Use Your Fine-Tuned Model

Once training completes, you'll get a model ID like:
```
ft:gpt-4o-mini-2024-07-18:your-org:custom-model:abc123
```

### **Update .env file:**

```env
OPENAI_MODEL=ft:gpt-4o-mini-2024-07-18:your-org:custom-model:abc123
```

### **Restart the server:**

```powershell
# Stop current server
Get-Process -Name node | Stop-Process -Force

# Start with new model
& "C:\Program Files\nodejs\node.exe" server.js
```

---

## 💰 Cost Estimate

- **Training**: ~$0.008 per 1K tokens
- **Usage**: ~$0.003 per 1K input tokens, ~$0.006 per 1K output tokens

**Example:**
- 50 examples × 1000 tokens each = 50K tokens
- Training cost: 50 × $0.008 = **$0.40**
- Usage: Same as gpt-4o-mini (very cheap)

---

## 📊 Training Data Best Practices

### **Quality Over Quantity**

- ✅ 10-50 high-quality examples > 100 poor examples
- ✅ Each example should be complete and correct
- ✅ Cover different scenarios (positive, negative, edge cases)
- ✅ Include various forms and workflows

### **Example Variety**

Include examples for:
1. **Different forms**: HSD, CBD, SORH, etc.
2. **Different workflows**: Login, navigation, form completion, submission
3. **Different field types**: Text, dropdown, checkbox, numeric
4. **Different page counts**: Single page, multi-page forms
5. **Different validations**: Success, error handling

### **Consistent Format**

All examples should:
- Use same section header format (# Section Name)
- Use same action format (Click "Element", Type "value" into "Field")
- Include Wait statements consistently
- Use CSV placeholders (%ColumnName%)

---

## 🎯 Example Training Data Structure

```jsonl
{"messages": [{"role": "system", "content": "You are a QA automation engineer generating detailed Salesforce test automation steps."}, {"role": "user", "content": "HSD form with 20 fields on page 1"}, {"role": "assistant", "content": "[Complete 50+ step workflow]"}]}
{"messages": [{"role": "system", "content": "You are a QA automation engineer generating detailed Salesforce test automation steps."}, {"role": "user", "content": "CBD form with validation errors"}, {"role": "assistant", "content": "[Complete workflow with error handling]"}]}
{"messages": [{"role": "system", "content": "You are a QA automation engineer generating detailed Salesforce test automation steps."}, {"role": "user", "content": "SORH form multi-page submission"}, {"role": "assistant", "content": "[Complete multi-page workflow]"}]}
```

---

## ✅ Validation

Before uploading, validate your JSONL file:

```javascript
// validate-training-data.js
const fs = require('fs');

const lines = fs.readFileSync('training-data.jsonl', 'utf8').split('\n').filter(l => l.trim());

console.log(`📊 Total examples: ${lines.length}`);

lines.forEach((line, idx) => {
    try {
        const obj = JSON.parse(line);
        if (!obj.messages || obj.messages.length !== 3) {
            console.error(`❌ Line ${idx + 1}: Invalid structure`);
        }
        if (obj.messages[2].content.length < 500) {
            console.warn(`⚠️  Line ${idx + 1}: Response seems short (${obj.messages[2].content.length} chars)`);
        }
    } catch (e) {
        console.error(`❌ Line ${idx + 1}: Invalid JSON`);
    }
});

console.log('✅ Validation complete');
```

Run: `node validate-training-data.js`

---

## 🔄 Iteration

After fine-tuning:

1. **Test the model** - Generate a few test cases
2. **Identify issues** - What's missing or wrong?
3. **Add more examples** - Address the issues
4. **Re-train** - Create a new fine-tuned model
5. **Compare** - Test both models and keep the better one

---

## 📞 Support

If you encounter issues:

1. Check OpenAI fine-tuning docs: https://platform.openai.com/docs/guides/fine-tuning
2. Validate your JSONL format
3. Ensure you have enough examples (minimum 10)
4. Check your API key has fine-tuning permissions

---

## 🎓 Alternative: Use Examples (No Fine-Tuning)

If you don't want to fine-tune, you can still get good results by:

1. **Always paste complete examples** in the "Example Test Steps" field
2. **Provide detailed descriptions** with all field names
3. **Use templates** from the templates folder
4. **Increase MAX_TOKENS** to 8000-16000

This works well but requires pasting examples every time.

---

**Fine-tuning gives you the best, most consistent results!** 🚀
