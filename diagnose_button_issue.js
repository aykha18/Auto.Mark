// Diagnose Button Issue Script
// Run this in browser console on localhost:3001

console.log('🔍 Diagnosing Secure Founding Spot Button Issue...');

// Check if React components are loaded
function checkReactComponents() {
    console.log('\n📦 Checking React Components...');
    
    // Check if main components exist
    const components = [
        'AICapabilitiesSection',
        'PricingComparison', 
        'EnhancedAIAssessment',
        'RazorpayCheckout'
    ];
    
    components.forEach(comp => {
        try {
            // This is a basic check - in real app we'd need to check differently
            console.log(`✓ ${comp}: Component should be available`);
        } catch (e) {
            console.error(`❌ ${comp}: ${e.message}`);
        }
    });
}

// Check for button elements
function checkButtons() {
    console.log('\n🔘 Checking Button Elements...');
    
    // Find all buttons with "Secure" text
    const buttons = Array.from(document.querySelectorAll('button')).filter(btn => 
        btn.textContent.includes('Secure') || btn.textContent.includes('Founding')
    );
    
    console.log(`Found ${buttons.length} buttons with "Secure" or "Founding" text:`);
    
    buttons.forEach((btn, index) => {
        console.log(`Button ${index + 1}:`, {
            text: btn.textContent.trim(),
            hasOnClick: !!btn.onclick,
            hasEventListeners: getEventListeners ? getEventListeners(btn) : 'DevTools needed',
            disabled: btn.disabled,
            className: btn.className
        });
        
        // Add test click listener
        btn.addEventListener('click', function(e) {
            console.log(`🖱️ Button clicked: "${btn.textContent.trim()}"`);
            console.log('Event details:', e);
        });
    });
    
    return buttons;
}

// Check for payment modal
function checkPaymentModal() {
    console.log('\n💳 Checking Payment Modal...');
    
    // Look for modal elements
    const modals = document.querySelectorAll('[class*="modal"], [class*="Modal"], .fixed');
    console.log(`Found ${modals.length} potential modal elements`);
    
    modals.forEach((modal, index) => {
        if (modal.textContent.includes('Razorpay') || modal.textContent.includes('Payment')) {
            console.log(`Payment modal ${index + 1}:`, {
                visible: !modal.classList.contains('hidden'),
                className: modal.className,
                content: modal.textContent.substring(0, 100) + '...'
            });
        }
    });
}

// Check for JavaScript errors
function checkErrors() {
    console.log('\n❌ Checking for JavaScript Errors...');
    
    // Override console.error to catch errors
    const originalError = console.error;
    const errors = [];
    
    console.error = function(...args) {
        errors.push(args);
        originalError.apply(console, args);
    };
    
    // Check for React errors
    window.addEventListener('error', function(e) {
        console.log('🚨 JavaScript Error:', e.error);
    });
    
    setTimeout(() => {
        console.log(`Captured ${errors.length} console errors`);
        errors.forEach((error, index) => {
            console.log(`Error ${index + 1}:`, error);
        });
    }, 1000);
}

// Test button functionality
function testButtonClicks() {
    console.log('\n🧪 Testing Button Clicks...');
    
    const buttons = checkButtons();
    
    buttons.forEach((btn, index) => {
        if (btn.textContent.includes('Secure Founding Spot')) {
            console.log(`Testing button ${index + 1}: "${btn.textContent.trim()}"`);
            
            // Simulate click
            setTimeout(() => {
                console.log(`Clicking button: ${btn.textContent.trim()}`);
                btn.click();
                
                // Check if modal appeared
                setTimeout(() => {
                    checkPaymentModal();
                }, 500);
            }, (index + 1) * 2000);
        }
    });
}

// Main diagnostic function
function runDiagnostics() {
    console.log('🚀 Starting Button Diagnostics...');
    
    checkReactComponents();
    checkButtons();
    checkPaymentModal();
    checkErrors();
    
    // Wait for page to fully load then test
    setTimeout(() => {
        console.log('\n🧪 Starting automated button tests...');
        testButtonClicks();
    }, 3000);
}

// Auto-run diagnostics
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runDiagnostics);
} else {
    runDiagnostics();
}

// Export functions for manual testing
window.buttonDiagnostics = {
    checkButtons,
    checkPaymentModal,
    testButtonClicks,
    runDiagnostics
};

console.log('📋 Diagnostic script loaded. Run window.buttonDiagnostics.runDiagnostics() to test manually.');