#!/usr/bin/env python3

# Test script to verify police signup functionality
import sys
import os
import json

def test_police_signup_implementation():
    """Test that the police signup has been properly fixed"""
    
    # Check that the HTML file no longer has inline JavaScript with wrong endpoint
    html_file = "C:/Users/student/OneDrive/Desktop/police_security_ai/frontend/police/police_signup.html"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # The HTML should only have the external JS reference, no inline form submission code
    has_old_auth_endpoint = "auth/signup/police" in html_content
    has_inline_form_handler = "document.getElementById(\"signupForm\").addEventListener" in html_content
    
    print("=== Police Signup Implementation Test ===")
    print(f"HTML contains old auth endpoint: {has_old_auth_endpoint}")
    print(f"HTML contains inline form handler: {has_inline_form_handler}")
    
    # Check external JS file
    js_file = "C:/Users/student/OneDrive/Desktop/police_security_ai/frontend/police/police_signup.js"
    
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    has_correct_endpoint = "users/signup/police" in js_content
    has_form_handler = "document.getElementById(\"signupForm\").addEventListener" in js_content
    has_redirect = "police_login.html" in js_content
    
    print(f"JS contains correct endpoint: {has_correct_endpoint}")
    print(f"JS contains form handler: {has_form_handler}")
    print(f"JS contains redirect to login: {has_redirect}")
    
    if has_correct_endpoint and has_form_handler and has_redirect and not has_old_auth_endpoint and not has_inline_form_handler:
        print("\n✅ Police signup implementation is correct!")
        print("   - Uses correct API endpoint: users/signup/police")
        print("   - Has proper form submission handler")
        print("   - Redirects to police_login.html after signup")
        print("   - No conflicting inline JavaScript")
        return True
    else:
        print("\n❌ Police signup implementation has issues")
        return False

if __name__ == "__main__":
    success = test_police_signup_implementation()
    sys.exit(0 if success else 1)