/**
 * Validation script for fine-tuning training data
 * 
 * Usage: node validate-training-data.js
 */

const fs = require('fs');

console.log('🔍 Validating training-data.jsonl...\n');

if (!fs.existsSync('training-data.jsonl')) {
    console.error('❌ training-data.jsonl not found!');
    console.log('Run: node create-training-data.js first');
    process.exit(1);
}

const content = fs.readFileSync('training-data.jsonl', 'utf8');
const lines = content.split('\n').filter(l => l.trim());

console.log(`📊 Total examples: ${lines.length}\n`);

let errors = 0;
let warnings = 0;

lines.forEach((line, idx) => {
    const lineNum = idx + 1;
    
    try {
        const obj = JSON.parse(line);
        
        // Check structure
        if (!obj.messages || !Array.isArray(obj.messages)) {
            console.error(`❌ Line ${lineNum}: Missing or invalid 'messages' array`);
            errors++;
            return;
        }
        
        if (obj.messages.length !== 3) {
            console.error(`❌ Line ${lineNum}: Expected 3 messages (system, user, assistant), got ${obj.messages.length}`);
            errors++;
            return;
        }
        
        // Check roles
        const roles = obj.messages.map(m => m.role);
        if (roles[0] !== 'system' || roles[1] !== 'user' || roles[2] !== 'assistant') {
            console.error(`❌ Line ${lineNum}: Invalid roles. Expected [system, user, assistant], got [${roles.join(', ')}]`);
            errors++;
            return;
        }
        
        // Check content
        const systemContent = obj.messages[0].content;
        const userContent = obj.messages[1].content;
        const assistantContent = obj.messages[2].content;
        
        if (!systemContent || systemContent.length < 50) {
            console.warn(`⚠️  Line ${lineNum}: System message seems short (${systemContent?.length || 0} chars)`);
            warnings++;
        }
        
        if (!userContent || userContent.length < 20) {
            console.warn(`⚠️  Line ${lineNum}: User request seems short (${userContent?.length || 0} chars)`);
            warnings++;
        }
        
        if (!assistantContent || assistantContent.length < 500) {
            console.warn(`⚠️  Line ${lineNum}: Assistant response seems short (${assistantContent?.length || 0} chars) - should be 50-100+ steps`);
            warnings++;
        }
        
        // Check for section headers
        if (!assistantContent.includes('# ')) {
            console.warn(`⚠️  Line ${lineNum}: No section headers found (should use # for sections)`);
            warnings++;
        }
        
        // Check for wait statements
        if (!assistantContent.includes('Wait for')) {
            console.warn(`⚠️  Line ${lineNum}: No wait statements found`);
            warnings++;
        }
        
        // Count steps
        const stepCount = assistantContent.split('\n').filter(l => 
            l.startsWith('Click ') || 
            l.startsWith('Type ') || 
            l.startsWith('Select ') || 
            l.startsWith('Verify ') ||
            l.startsWith('Navigate ')
        ).length;
        
        if (stepCount < 20) {
            console.warn(`⚠️  Line ${lineNum}: Only ${stepCount} action steps found (should have 50-100+)`);
            warnings++;
        }
        
        console.log(`✅ Line ${lineNum}: Valid (${stepCount} action steps, ${assistantContent.length} chars)`);
        
    } catch (e) {
        console.error(`❌ Line ${lineNum}: Invalid JSON - ${e.message}`);
        errors++;
    }
});

console.log('\n' + '='.repeat(60));
console.log('📊 Validation Summary:');
console.log(`   Total examples: ${lines.length}`);
console.log(`   ✅ Valid: ${lines.length - errors}`);
console.log(`   ❌ Errors: ${errors}`);
console.log(`   ⚠️  Warnings: ${warnings}`);

if (errors > 0) {
    console.log('\n❌ Fix errors before uploading to OpenAI');
    process.exit(1);
} else if (warnings > 0) {
    console.log('\n⚠️  Consider addressing warnings for better results');
} else {
    console.log('\n✅ All examples are valid!');
}

console.log('\n📤 Ready to upload:');
console.log('openai api fine_tuning.jobs.create -t training-data.jsonl -m gpt-4o-mini-2024-07-18');
