# Gherkin to Automation Steps Converter - Complete Guide

## Overview

The Gherkin converter works with **any** `.feature` file and converts Gherkin scenarios into detailed automation test steps in your exact format.

---

## ✅ Supported Gherkin Formats

The converter handles all standard Gherkin syntax:

### 1. **Text Input Fields**
```gherkin
When the user enters "value" into "Field Name"
And the user enters "123" into "Number Field"
```
**Output:**
```
Type "%Field Name%" into "Field Name"
Wait for 1 seconds
Type "%Number Field%" into "Number Field"
Wait for 1 seconds
```

### 2. **Dropdown/Select Fields**
```gherkin
And the user selects "Yes" for "Articles"
And the user selects "Option" for "Dropdown Name"
```
**Output:**
```
Select "%Articles%" from Dropdown "Articles"
Wait for 1 seconds
Select "%Dropdown Name%" from Dropdown "Dropdown Name"
Wait for 1 seconds
```

### 3. **Textarea Fields**
```gherkin
And the user enters "Long text" into textarea "Comments"
And the user enters "Description" into textarea "Description Field"
```
**Output:**
```
Fill textarea "%Comments%" with "Comments"
Wait for 1 seconds
Fill textarea "%Description Field%" with "Description Field"
Wait for 1 seconds
```

### 4. **Button Clicks**
```gherkin
And the user clicks "Submit"
And the user clicks "Next"
When I click on "Save" button
```
**Output:**
```
Click "Submit"
Wait for 1 seconds
Click "Next"
Wait for 1 seconds
Click "Save"
Wait for 1 seconds
```

### 5. **Navigation**
```gherkin
When the user navigates to "Dashboard"
And the user opens "Reports Section"
```
**Output:**
```
Click "Dashboard"
Wait for 1 seconds
Click "Reports Section"
Wait for 1 seconds
```

---

## 📁 Example Feature Files

### Example 1: Login Feature
```gherkin
Feature: User Login

Scenario: Successful login with valid credentials
  Given the user is on the login page
  When the user enters "admin@example.com" into "Email"
  And the user enters "password123" into "Password"
  And the user clicks "Login"
  Then the user should see "Dashboard"
```

**Generated Output:**
```
Type "%Email%" into "Email"
Wait for 1 seconds
Type "%Password%" into "Password"
Wait for 1 seconds
Click "Login"
Wait for 1 seconds
Click "Dashboard"
Wait for 1 seconds
```

---

### Example 2: Form Submission Feature
```gherkin
Feature: Contact Form Submission

Scenario: Submit contact form with all fields
  Given the user is on the contact page
  When the user enters "John Doe" into "Full Name"
  And the user enters "john@example.com" into "Email Address"
  And the user enters "555-1234" into "Phone Number"
  And the user selects "General Inquiry" for "Subject"
  And the user enters "I have a question" into textarea "Message"
  And the user clicks "Submit"
```

**Generated Output:**
```
Type "%Full Name%" into "Full Name"
Wait for 1 seconds
Type "%Email Address%" into "Email Address"
Wait for 1 seconds
Type "%Phone Number%" into "Phone Number"
Wait for 1 seconds
Select "%Subject%" from Dropdown "Subject"
Wait for 1 seconds
Fill textarea "%Message%" with "Message"
Wait for 1 seconds
Click "Submit"
Wait for 1 seconds
```

---

### Example 3: E-commerce Feature
```gherkin
Feature: Product Purchase

Scenario: Add product to cart and checkout
  Given the user is on the products page
  When the user clicks "Electronics"
  And the user clicks "Laptop"
  And the user selects "2" for "Quantity"
  And the user clicks "Add to Cart"
  And the user clicks "Checkout"
  And the user enters "John Smith" into "Billing Name"
  And the user enters "123 Main St" into "Address"
  And the user enters "New York" into "City"
  And the user selects "NY" for "State"
  And the user enters "10001" into "Zip Code"
  And the user enters "4111111111111111" into "Card Number"
  And the user clicks "Place Order"
```

**Generated Output:**
```
Click "Electronics"
Wait for 1 seconds
Click "Laptop"
Wait for 1 seconds
Select "%Quantity%" from Dropdown "Quantity"
Wait for 1 seconds
Click "Add to Cart"
Wait for 1 seconds
Click "Checkout"
Wait for 1 seconds
Type "%Billing Name%" into "Billing Name"
Wait for 1 seconds
Type "%Address%" into "Address"
Wait for 1 seconds
Type "%City%" into "City"
Wait for 1 seconds
Select "%State%" from Dropdown "State"
Wait for 1 seconds
Type "%Zip Code%" into "Zip Code"
Wait for 1 seconds
Type "%Card Number%" into "Card Number"
Wait for 1 seconds
Click "Place Order"
Wait for 1 seconds
```

---

### Example 4: Multi-Page Form Feature
```gherkin
Feature: Employee Registration

Scenario: Complete multi-page employee registration
  Given the user is on the registration page
  
  # Page 1: Personal Information
  When the user enters "Jane Doe" into "Full Name"
  And the user enters "jane.doe@company.com" into "Work Email"
  And the user enters "555-9876" into "Phone"
  And the user selects "Engineering" for "Department"
  And the user clicks "Next"
  
  # Page 2: Employment Details
  And the user enters "Software Engineer" into "Job Title"
  And the user selects "Full-time" for "Employment Type"
  And the user enters "2024-01-15" into "Start Date"
  And the user selects "John Manager" for "Reporting Manager"
  And the user clicks "Next"
  
  # Page 3: Additional Information
  And the user enters "5 years experience in web development" into textarea "Background"
  And the user selects "Yes" for "Remote Work"
  And the user clicks "Submit"
```

**Generated Output:**
```
Type "%Full Name%" into "Full Name"
Wait for 1 seconds
Type "%Work Email%" into "Work Email"
Wait for 1 seconds
Type "%Phone%" into "Phone"
Wait for 1 seconds
Select "%Department%" from Dropdown "Department"
Wait for 1 seconds
Click "Next"
Wait for 1 seconds
Type "%Job Title%" into "Job Title"
Wait for 1 seconds
Select "%Employment Type%" from Dropdown "Employment Type"
Wait for 1 seconds
Type "%Start Date%" into "Start Date"
Wait for 1 seconds
Select "%Reporting Manager%" from Dropdown "Reporting Manager"
Wait for 1 seconds
Click "Next"
Wait for 1 seconds
Fill textarea "%Background%" with "Background"
Wait for 1 seconds
Select "%Remote Work%" from Dropdown "Remote Work"
Wait for 1 seconds
Click "Submit"
Wait for 1 seconds
```

---

## 🎯 How to Use with Different Feature Files

### **Step 1: Prepare Your Feature File**

Create any `.feature` file with standard Gherkin syntax:
- Use `Given`, `When`, `And`, `Then` keywords
- Use quotes around values and field names
- Use `into` for text fields
- Use `for` for dropdowns
- Use `into textarea` for textarea fields

### **Step 2: Upload or Paste**

**Option A: Upload File**
1. Go to http://localhost:3000/gherkin
2. Drag & drop your `.feature` file
3. Click "Generate Automation Steps"

**Option B: Paste Text**
1. Go to http://localhost:3000/gherkin
2. Copy your Gherkin scenario
3. Paste into the text area
4. Click "Generate Automation Steps"

### **Step 3: Get Output**

The system will generate automation steps in your exact format:
- Text fields → `Type "%Field%" into "Field"`
- Dropdowns → `Select "%Field%" from Dropdown "Field"`
- Textareas → `Fill textarea "%Field%" with "Field"`
- Buttons → `Click "Button"`
- Wait → `Wait for 1 seconds` (after every action)

### **Step 4: Copy or Download**

- Click "Copy Steps" to copy to clipboard
- Click "Download TXT" to save as a file

---

## 🔧 Special Cases Handled

### 1. **Other-Specify Fields**
```gherkin
And the user enters "Custom value" into "Other-Specify"
```
**Output:**
```
Type "%Other-Specify%" into "Other-Specify"
Wait for 1 seconds
```
(Uses Type, not Select)

### 2. **Textarea Detection**
```gherkin
And the user enters "Long text" into textarea "Comments"
```
**Output:**
```
Fill textarea "%Comments%" with "Comments"
Wait for 1 seconds
```

### 3. **Field Names with Special Characters**
```gherkin
And the user enters "100" into "Number of people on listserv"
And the user selects "Yes" for "Is the audience/membership for the listserv the same as for the newsletter?"
```
**Output:**
```
Type "%Number of people on listserv%" into "Number of people on listserv"
Wait for 1 seconds
Select "%Is the audience/membership for the listserv the same as for the newsletter?%" from Dropdown "Is the audience/membership for the listserv the same as for the newsletter?"
Wait for 1 seconds
```

### 4. **Comments in Gherkin**
```gherkin
# This is a comment
And the user clicks "Next"
```
**Output:**
```
Click "Next"
Wait for 1 seconds
```
(Comments are preserved or ignored as needed)

---

## 📋 Format Rules (Always Applied)

1. **CSV Placeholders:** `%FieldName%` (no quotes inside percent signs)
2. **Field Names:** Always use the field name, not the value
3. **Wait Statements:** Added after every action
4. **Dropdown Format:** `Select "%Field%" from Dropdown "Field"` (capital D)
5. **Textarea Format:** `Fill textarea "%Field%" with "Field"`
6. **Type Format:** `Type "%Field%" into "Field"`
7. **Click Format:** `Click "Button"`

---

## 🚀 Works With Any Application

The converter is **application-agnostic** and works with:

✅ Salesforce applications  
✅ Web forms  
✅ E-commerce sites  
✅ Admin panels  
✅ CRM systems  
✅ Custom applications  
✅ Any web application with forms and buttons  

**As long as your Gherkin follows standard syntax, the converter will work!**

---

## 💡 Tips for Best Results

1. **Use clear field names** in your Gherkin
2. **Specify "textarea"** when using textarea fields
3. **Use consistent naming** across your feature files
4. **Include all steps** - the converter handles any number of steps
5. **Test with sample data** first to verify the format

---

## 🔗 Quick Links

- **Gherkin Converter UI:** http://localhost:3000/gherkin
- **Original Test Generator:** http://localhost:3000

---

## 📞 Need Help?

If you have a specific feature file format that's not working:
1. Check the Gherkin syntax is correct
2. Ensure field names are in quotes
3. Use `into` for text fields and `for` for dropdowns
4. Specify `textarea` for textarea fields

The converter is designed to be flexible and work with any standard Gherkin format!
