#!/usr/bin/env python3
"""
Download required NLTK data for the application.
This script is run during deployment to ensure all NLTK resources are available.
"""
import nltk
import ssl

# Handle SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download required NLTK data
print("Downloading NLTK data...")
try:
    nltk.download('punkt', quiet=False)
    print("✓ Downloaded punkt")
except Exception as e:
    print(f"✗ Failed to download punkt: {e}")

try:
    nltk.download('punkt_tab', quiet=False)
    print("✓ Downloaded punkt_tab")
except Exception as e:
    print(f"✗ Failed to download punkt_tab: {e}")

print("NLTK data download complete!")
