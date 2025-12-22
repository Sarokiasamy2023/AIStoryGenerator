/**
 * Helper script to create fine-tuning training data
 * 
 * Usage:
 * 1. Add your examples in the 'examples' array below
 * 2. Run: node create-training-data.js
 * 3. Upload training-data.jsonl to OpenAI for fine-tuning
 */

const fs = require('fs');

// Add your examples here
const examples = [
    {
        userRequest: "Generate detailed test steps for completing HSD Performance Report form HSD-01059 with all pages including login, navigation, all form fields, and submission",
        assistantResponse: `# Salesforce HSD Performance Reports - Complete Workflow Test
 
# Login
Navigate to https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/
Wait for 2 seconds
Type "sarokiasamy2@dmigs.com.dcp.dcpuat" into Username
Type "Grantee@456" into Password
Click "Log in"
Wait for 2 seconds
 
# Agreement Page
Click "I Disagree"
Click "Next"
Wait for 2 seconds
Click "Next"
Click "Finish"
Wait for 3 seconds
 
# Navigate to HSD Performance Reports
Click "HSD PERFORMANCE REPORTS"
Wait for 2 seconds
Click "Recently Viewed"
Wait for 1 seconds
Click "In Progress Reports"
Wait for 2 seconds
Click "HSD-01059"
Wait for 1 seconds
 
# Start/Edit Form
Click "Edit"
Wait for 2 seconds
Click "Next"
 
# Complete Form - Page 1
Type "5110" into "Number of people on listserv"
Type "0" into "Number of people receiving newsletter (via mail or electronic)"
Type "0" into "How many newsletter issues per year (if known)?"
Type "54" into "How many listserv posts distributed per year (if known)?"
Type "22016" into "Number of website hits- Specify most popular sections of websites (if known) - Value"
Type "The most popular sections were: (1) Hawaii State Office of Primary Care & Rural Health: Home Page, FQHC, HPSA, MUA/MUP; (2) Hawaii State Rural Health Association: Home Page, About, Programs, Membership; and (3) Project ECHO Hawaii: Home Page, Register, Behavioral Health ECHO Resources, What is ECHO?" into "Number of website hits- Specify most popular sections of websites (if known) - Specify(Allows 2000 characters)"
Select "No" from "Is the audience/membership for the listserv the same as for the newsletter?"
Select "Interactive" from "Is the listserv one-way information or interactive?"
Select "NA/None" from "Articles"
Select "Hosted or Co-Hosted" from "Conferences (hosted or co-hosted)"
Select "New" from "Fact Sheets"
Select "New" from "Maps"
Select "New" from "Newsletter"
Select "New" from "Toolkits"
Select "New" from "Webinars"
Select "New" from "Websites"
Type "The Hawaii State Office of Primary Care & Rural Health, in partnership with the Hawaii State Rural Health Association, has completed a Maui Together Wildfire Assessment." into "Describe one tool that you created to address a problem in your state."
Click "Next"
Wait for 1 seconds
 
# Complete Form - Page 2
Select "New" from "Behavioral Health"
Select "New" from "Community Development"
Select "New" from "Grant Writing"
Select "New" from "Needs Assesment"
Select "New" from "Older Adults/Aging"
Select "New" from "Opioids"
Select "New" from "Oral Health"
Select "New" from "Population health"
Select "New" from "Rural Health Network"
Select "New" from "Telehealth"
Select "New" from "Transportation"
Select "New" from "Tribals"
Select "New" from "Veterans"
Select "New" from "Workforce"
Select "New" from "Other"
Type "Sample comment" into "Other-Specify (Allows 2000 characters)"
Check "Critical Access Hospitals" checkbox
Type "Test" into "Collaborative effort in your state"
Click "Next"
Wait for 1 seconds

# Complete Form - Page 3
Type "107" into "Face to Face"
Type "Test" into "Face to Face description"
Type "49" into "Academic Institutions"
Type "Test" into "Academic Institutions Description"
Click "Next"
Wait for 1 seconds
 
# Upload and Comments
Click "Upload"
Type "comment text" into "Comments"
 
# Submit for Approval
Click "Next"
Wait for 1 seconds
Verify "Submit" is visible
Click "Submit"
Wait for 3 seconds
Verify "Form submitted successfully"`
    },
    {
        userRequest: "Generate test steps for CBD Performance Reports Form 1 Demographics with Counties Served, Full Patient Panel, and Target Population Measures fields",
        assistantResponse: `# CBD Performance Reports - Form 1 Demographics
 
# Login
Navigate to https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/
Wait for 2 seconds
Type "%Username%" into Username
Type "%Password%" into Password
Click "Log in"
Wait for 2 seconds
 
# Navigate to CBD Performance Reports
Click "CBD PERFORMANCE REPORTS"
Wait for 1 seconds
Click "Recently Viewed"
Wait for 1 seconds
Click "CBD-01361"
Wait for 2 seconds
Click "Form 1: Demographics"
Wait for 2 seconds

# Generate CSV
Wait for 30 seconds

Verify "An agency may not conduct or sponsor, and a person is not required to respond to, a collection of information unless it displays a currently valid OMB control number. The OMB control number for this project is 0915-0387. Public reporting burden for this collection of information is estimated to average 22 hours per response, including the time for reviewing instructions, searching existing data sources, and completing and reviewing the collection of information. Send comments regarding this burden estimate or any other aspect of this collection of information, including suggestions for reducing this burden, to HRSA Reports Clearance Officer, 5600 Fishers Lane, Room 14N-39, Rockville, Maryland, 20857."

Click "Next"
Wait for 2 seconds

# Complete Form Fields
Type "%Number of Counties Served%" into "Number of Counties Served"
Type "%Counties Served%" into "Please specify the names of the counties served."
Type "%Full Patient Panel%" into "Number of people in the Full Patient Panel"
Select "%Target Population Measures%" from "Changes to Target Population Measures"

# Save Form
Click "Save"
Wait for 3 seconds
Verify "Form saved successfully"`
    }
    
    // ADD MORE EXAMPLES HERE (aim for 10-50 total)
    // Copy your existing test cases and paste them in this format
];

// System message for all examples
const systemMessage = "You are a QA automation engineer generating detailed Salesforce test automation steps. Always include section headers using #, complete navigation flows, all form fields, wait statements after every action, and CSV placeholders for data values. Generate 50-100+ comprehensive steps.";

// Convert to JSONL format
const jsonl = examples.map(ex => JSON.stringify({
    messages: [
        {
            role: "system",
            content: systemMessage
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

// Write to file
fs.writeFileSync('training-data.jsonl', jsonl);

// Statistics
console.log('✅ Training data created: training-data.jsonl');
console.log(`📊 Total examples: ${examples.length}`);
console.log(`📏 Average response length: ${Math.round(examples.reduce((sum, ex) => sum + ex.assistantResponse.length, 0) / examples.length)} characters`);
console.log('');
console.log('Next steps:');
console.log('1. Add more examples to this file (aim for 10-50 total)');
console.log('2. Run: node create-training-data.js again');
console.log('3. Validate: node validate-training-data.js');
console.log('4. Upload to OpenAI for fine-tuning');
console.log('');
console.log('Upload command:');
console.log('openai api fine_tuning.jobs.create -t training-data.jsonl -m gpt-4o-mini-2024-07-18');
