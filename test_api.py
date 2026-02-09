#!/usr/bin/env python3
"""
Comprehensive API Test Suite for AI Summarizer
Tests all endpoints, styles, file uploads, and edge cases
"""

import requests
import os
import time

BASE_URL = "http://localhost:8000/api"

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_separator():
    print("-" * 80)

# Sample text for testing
SAMPLE_TEXT = """
Artificial intelligence (AI) has revolutionized the way we interact with technology and 
process information in the modern world. Machine learning, a subset of AI, enables computers 
to learn from data without being explicitly programmed, leading to breakthroughs in various 
fields such as healthcare, finance, and transportation. Deep learning, which uses neural 
networks with multiple layers, has particularly excelled in tasks like image recognition, 
natural language processing, and speech synthesis. Companies worldwide are investing heavily 
in AI research and development, recognizing its potential to automate complex tasks, improve 
decision-making processes, and create innovative products and services. However, the rapid 
advancement of AI also raises important ethical questions about privacy, job displacement, 
algorithmic bias, and the need for responsible AI governance. As we continue to integrate 
AI into our daily lives, it becomes crucial to balance technological progress with human 
values and societal well-being.
""" * 3  # ~450 words

def test_health_check():
    """Test API health endpoint"""
    print_header("1. HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"✓ API is running: {response.json()}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        return False

def test_input_validation():
    """Test input validation rules"""
    print_header("2. INPUT VALIDATION")
    
    # Test 1: Text too short
    print("\nTest 2.1: Text too short (< 150 words)")
    short_text = "AI is transforming the world. " * 10  # ~70 words
    response = requests.post(
        f"{BASE_URL}/summarize",
        json={"text": short_text, "style": "brief"}
    )
    if response.status_code == 400:
        print(f"✓ Correctly rejected: {response.json()['detail']}")
    else:
        print(f"✗ Should have rejected short text")
    
    # Test 2: Text too long for text area
    print("\nTest 2.2: Text too long (> 1500 words)")
    long_text = SAMPLE_TEXT * 5  # ~2250 words
    response = requests.post(
        f"{BASE_URL}/summarize",
        json={"text": long_text, "style": "brief"}
    )
    if response.status_code == 400:
        print(f"✓ Correctly rejected: {response.json()['detail']}")
    else:
        print(f"✗ Should have rejected long text")
    
    # Test 3: Valid text
    print("\nTest 2.3: Valid text (150-1500 words)")
    response = requests.post(
        f"{BASE_URL}/summarize",
        json={"text": SAMPLE_TEXT, "style": "brief"}
    )
    if response.status_code == 200:
        print(f"✓ Accepted valid text")
    else:
        print(f"✗ Should have accepted valid text")

def test_all_styles():
    """Test all summarization styles"""
    print_header("3. SUMMARIZATION STYLES")
    
    word_count = len(SAMPLE_TEXT.split())
    
    styles = [
        ("brief", "Condenses to 1-2 sentences"),
        ("detailed", "Comprehensive summary"),
        ("bullet_points", "Formatted as bullets"),
    ]
    
    for style, description in styles:
        print(f"\nTest 3.{styles.index((style, description)) + 1}: {style.upper()}")
        print(f"Description: {description}")
        print_separator()
        
        response = requests.post(
            f"{BASE_URL}/summarize",
            json={"text": SAMPLE_TEXT, "style": style}
        )
        
        if response.status_code == 200:
            result = response.json()
            compression = result['word_count'] / word_count * 100
            print(f"✓ Success")
            print(f"  Original: {word_count} words")
            print(f"  Summary: {result['word_count']} words ({compression:.1f}%)")
            print(f"  Preview: {result['summary'][:100]}...")
        else:
            print(f"✗ Failed: {response.json()}")

def test_custom_styles():
    """Test custom style with different prompts"""
    print_header("4. CUSTOM STYLES")
    
    custom_prompts = [
        ("Academic", "Rewrite as an academic abstract with formal language"),
        ("Social Media", "Rewrite as an engaging tweet (280 chars max)"),
        ("ELI5", "Explain to a 5-year-old using simple words"),
    ]
    
    for name, prompt in custom_prompts:
        print(f"\nTest 4.{custom_prompts.index((name, prompt)) + 1}: {name}")
        print(f"Prompt: {prompt}")
        print_separator()
        
        response = requests.post(
            f"{BASE_URL}/summarize",
            json={
                "text": SAMPLE_TEXT,
                "style": "custom",
                "custom_prompt": prompt
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success")
            print(f"  Summary: {result['summary'][:150]}...")
        else:
            print(f"✗ Failed: {response.json()}")

def test_file_uploads():
    """Test file upload functionality"""
    print_header("5. FILE UPLOADS")
    
    # Check if test_data directory exists
    if not os.path.exists("test_data"):
        print("⚠ test_data directory not found, skipping file upload tests")
        return
    
    test_files = [
        ("test_data/article1.txt", "brief", "Plain text file"),
        ("test_data/article2.md", "detailed", "Markdown file"),
        ("test_data/data.csv", "brief", "CSV file"),
        ("test_data/config.json", "brief", "JSON file"),
    ]
    
    for filepath, style, description in test_files:
        if not os.path.exists(filepath):
            print(f"\n⚠ {filepath} not found, skipping")
            continue
        
        print(f"\nTest 5.{test_files.index((filepath, style, description)) + 1}: {description}")
        print(f"File: {filepath}, Style: {style}")
        print_separator()
        
        try:
            with open(filepath, 'rb') as f:
                files = {'file': f}
                data = {'style': style}
                response = requests.post(
                    f"{BASE_URL}/summarize-file",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Success")
                print(f"  Summary: {result['summary'][:100]}...")
            else:
                print(f"✗ Failed: {response.json()}")
        except Exception as e:
            print(f"✗ Exception: {e}")

def test_chunking():
    """Test chunking with long text"""
    print_header("6. CHUNKING (LONG TEXT)")
    
    # Create text that triggers chunking (> 1500 words)
    long_text = SAMPLE_TEXT * 5  # ~2250 words
    word_count = len(long_text.split())
    
    print(f"\nTest 6.1: Long text chunking ({word_count} words)")
    print("Note: This should trigger hierarchical summarization")
    print_separator()
    
    # This should fail validation for text area but would work for file upload
    print("Testing with text area (should fail - max 1500 words):")
    response = requests.post(
        f"{BASE_URL}/summarize",
        json={"text": long_text, "style": "brief"}
    )
    
    if response.status_code == 400:
        print(f"✓ Correctly rejected for text area")
    else:
        print(f"✗ Should have rejected")

def test_error_handling():
    """Test error handling"""
    print_header("7. ERROR HANDLING")
    
    # Test 1: Missing text
    print("\nTest 7.1: Missing text")
    response = requests.post(
        f"{BASE_URL}/summarize",
        json={"style": "brief"}
    )
    if response.status_code in [400, 422]:
        print(f"✓ Correctly handled missing text")
    else:
        print(f"✗ Should have rejected")
    
    # Test 2: Invalid style
    print("\nTest 7.2: Invalid style")
    response = requests.post(
        f"{BASE_URL}/summarize",
        json={"text": SAMPLE_TEXT, "style": "invalid_style"}
    )
    if response.status_code in [400, 422]:
        print(f"✓ Correctly handled invalid style")
    else:
        print(f"✗ Should have rejected")
    
    # Test 3: Custom style without prompt
    print("\nTest 7.3: Custom style without prompt")
    response = requests.post(
        f"{BASE_URL}/summarize",
        json={"text": SAMPLE_TEXT, "style": "custom"}
    )
    if response.status_code == 400:
        print(f"✓ Correctly required custom_prompt")
    else:
        print(f"✗ Should have required custom_prompt")

def test_performance():
    """Test API performance"""
    print_header("8. PERFORMANCE")
    
    print("\nTest 8.1: Response time for brief summary")
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/summarize",
        json={"text": SAMPLE_TEXT, "style": "brief"}
    )
    elapsed = time.time() - start
    
    if response.status_code == 200:
        print(f"✓ Completed in {elapsed:.2f}s")
        if elapsed < 10:
            print("  Performance: Good")
        elif elapsed < 20:
            print("  Performance: Acceptable")
        else:
            print("  Performance: Slow (consider optimization)")
    else:
        print(f"✗ Failed")

def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*80)
    print("  AI SUMMARIZER - COMPREHENSIVE API TEST SUITE")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    if not test_health_check():
        print("\n⚠ API is not running. Please start the backend server.")
        return
    
    test_input_validation()
    test_all_styles()
    test_custom_styles()
    test_file_uploads()
    test_chunking()
    test_error_handling()
    test_performance()
    
    # Summary
    print_header("TEST SUITE COMPLETE")
    print(f"Finished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✓ All test categories executed")
    print("Review output above for detailed results")

if __name__ == "__main__":
    run_all_tests()
