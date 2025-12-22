# How to Get Detailed Automation Steps (50-100+ Steps)

## 🎯 The Key: Provide Detailed Test Case Information

The AI generates steps based on what you tell it. To get 50-100+ detailed steps, you need to provide detailed test case information.

---

## ✅ **Method 1: Detailed Description (Recommended)**

### **Instead of this (generates only 10-15 steps):**
```
Test Case ID: HSD_TC_001
Title: Complete HSD Performance Report
Description: Test the HSD form
Type: Positive
Priority: High
```

### **Do this (generates 50-100+ steps):**
```
Test Case ID: HSD_TC_001
Title: Complete HSD Performance Report Form - All Pages
Description: Test the complete workflow for HSD Performance Reports including:
- Login to Salesforce portal at https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/
- Navigate through agreement page
- Access HSD PERFORMANCE REPORTS module
- Select report HSD-01059 from Recently Viewed
- Complete Form Page 1 with fields:
  * Number of people on listserv
  * Number of people receiving newsletter (via mail or electronic)
  * How many newsletter issues per year (if known)?
  * How many listserv posts distributed per year (if known)?
  * Number of website hits
  * Specify most popular sections of websites (2000 char field)
  * Is the audience/membership for the listserv the same as for the newsletter? (dropdown)
  * Is the listserv one-way information or interactive? (dropdown)
  * Articles (dropdown)
  * Conferences hosted or co-hosted (dropdown)
  * Fact Sheets (dropdown)
  * Maps (dropdown)
  * Newsletter (dropdown)
  * Toolkits (dropdown)
  * Webinars (dropdown)
  * Websites (dropdown)
  * Describe one tool that you created (2000 char field)
- Complete Form Page 2 with fields:
  * Behavioral Health (dropdown)
  * Community Development (dropdown)
  * Grant Writing (dropdown)
  * Needs Assessment (dropdown)
  * Older Adults/Aging (dropdown)
  * Opioids (dropdown)
  * Oral Health (dropdown)
  * Population health (dropdown)
  * Rural Health Network (dropdown)
  * Telehealth (dropdown)
  * Transportation (dropdown)
  * Tribals (dropdown)
  * Veterans (dropdown)
  * Workforce (dropdown)
  * Other (dropdown)
  * Other-Specify (2000 char field)
  * Critical Access Hospitals (checkbox)
  * Collaborative effort in your state (text field)
- Complete Form Page 3 with fields:
  * Face to Face (number)
  * Face to Face description (text)
  * Academic Institutions (number)
  * Academic Institutions Description (text)
- Upload documents
- Add comments
- Submit for approval

Type: Positive
Priority: High
Preconditions: 
- Valid user credentials (username: sarokiasamy2@dmigs.com.dcp.dcpuat, password: Grantee@456)
- Report HSD-01059 exists and is in "In Progress" status
- User has edit permissions
```

---

## ✅ **Method 2: Use the Example Template**

Paste this into the **"Example Test Steps"** field:

```
# Salesforce HSD Performance Reports - Complete Workflow Test
 
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
Verify "Form submitted successfully"
```

---

## 📋 **Quick Checklist for Detailed Steps**

To get 50-100+ detailed steps, make sure you include:

### ✅ **In Test Case Description:**
1. **Login URL** - Full URL to the application
2. **Credentials** - Username and password (or CSV placeholders)
3. **Navigation path** - Every menu/button to click
4. **ALL form fields** - List every single field name
5. **Field types** - Specify if dropdown, text, checkbox, etc.
6. **Multi-page forms** - Mention "Page 1", "Page 2", etc.
7. **Validation** - What to verify at each step
8. **Submit process** - How to save/submit

### ✅ **In Example Test Steps:**
1. Paste a complete example from the template
2. Include all sections with # headers
3. Show the full workflow from login to submit
4. Include Wait statements after every action

---

## 🎯 **Example: CBD Form Demographics**

### **Detailed Description:**
```
Description: Complete CBD Performance Reports Form 1: Demographics workflow:
- Login to https://hrsa-dcpaas--dcpuat.sandbox.my.site.com/pars/s/login/
- Navigate to CBD PERFORMANCE REPORTS
- Select report CBD-01361 from Recently Viewed
- Open Form 1: Demographics
- Wait for OMB disclaimer (30 seconds for CSV generation)
- Verify OMB control number disclaimer text
- Click Next to proceed to form fields
- Complete all fields:
  * Number of Counties Served (numeric field)
  * Counties Served - specify names (text field, 2000 char limit)
  * Full Patient Panel (numeric field, 10 digits max, whole numbers only)
  * Changes to Target Population Measures (dropdown: Yes/No/N/A)
- Save the form
- Verify success message
```

### **Example Steps to Paste:**
```
# CBD Performance Reports - Form 1 Demographics
 
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

Verify "An agency may not conduct or sponsor, and a person is not required to respond to, a collection of information unless it displays a currently valid OMB control number. The OMB control number for this project is 0915-0387."

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
Verify "Form saved successfully"
```

---

## 🚀 **Pro Tips**

1. **List ALL fields** - Don't say "fill out the form", list every field name
2. **Use exact field labels** - Copy field names exactly as they appear
3. **Specify field types** - (dropdown), (checkbox), (text field), (numeric)
4. **Multi-page forms** - Mention each page and what fields are on it
5. **Include wait times** - Especially for slow-loading pages
6. **Add verifications** - What should appear after each major action
7. **Use CSV placeholders** - %FieldName% for data-driven testing

---

## ❌ **Common Mistakes**

### **Too Vague (generates only 10-15 steps):**
```
Description: Test the form submission
```

### **Better (generates 50-100+ steps):**
```
Description: Test complete form submission workflow including:
- Login with credentials
- Navigate to Reports module
- Select report XYZ-123
- Fill all 25 fields on Page 1: [list all field names]
- Fill all 18 fields on Page 2: [list all field names]
- Upload document
- Submit for approval
- Verify success
```

---

## 📊 **Expected Results**

With detailed input, you should get:

✅ **50-100+ automation steps**  
✅ **Section headers** (# Login, # Navigate, # Complete Form)  
✅ **Every field** listed individually  
✅ **Wait statements** after each action  
✅ **Verification steps** at key points  
✅ **CSV placeholders** for data values  
✅ **Complete workflow** from start to finish  

---

**The more detail you provide, the more detailed steps you get!** 🎯
