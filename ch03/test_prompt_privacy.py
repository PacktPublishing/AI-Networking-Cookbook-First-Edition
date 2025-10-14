#!/usr/bin/env python3
"""
Test script to check if an OpenAI prompt is private.
Tests both with and without API key authentication.
"""

import os
import sys
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv


def test_prompt_without_api_key() -> None:
    """Test the prompt without providing an API key."""
    print("=" * 60)
    print("TESTING WITHOUT API KEY")
    print("=" * 60)
    
    try:
        # Create client without API key
        client = OpenAI()
        
        print("Attempting to access prompt without API key...")
        response = client.responses.create(
            prompt={
                "id": "pmpt_687e603190188194baaf822fed2e3b690bcf8c7612f1ba4d",
                "version": "1"
            }
        )
        
        print("❌ SUCCESS - Prompt is NOT private (accessible without API key)")
        print(f"Response: {response}")
        
    except Exception as e:
        print("✅ SUCCESS - Prompt is private (requires authentication)")
        print(f"Error: {type(e).__name__}: {str(e)}")


def test_prompt_with_api_key() -> None:
    """Test the prompt with API key from .env file."""
    print("\n" + "=" * 60)
    print("TESTING WITH API KEY")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        return
    
    try:
        # Create client with API key
        client = OpenAI(api_key=api_key)
        
        print("Attempting to access prompt with API key...")
        response = client.responses.create(
            prompt={
                "id": "pmpt_687e603190188194baaf822fed2e3b690bcf8c7612f1ba4d",
                "version": "1"
            }
        )
        
        print("✅ SUCCESS - Prompt accessed successfully with API key")
        print(f"Response: {response}")
        
    except Exception as e:
        print("❌ ERROR - Failed to access prompt even with API key")
        print(f"Error: {type(e).__name__}: {str(e)}")


def main() -> None:
    """Main function to run both tests."""
    print("OpenAI Prompt Privacy Test")
    print("Testing prompt ID: pmpt_687e603190188194baaf822fed2e3b690bcf8c7612f1ba4d")
    print()
    
    # Test without API key
    test_prompt_without_api_key()
    
    # Test with API key
    test_prompt_with_api_key()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("If the first test shows 'SUCCESS - Prompt is private', then the prompt")
    print("requires authentication and is properly secured.")
    print("If the first test shows 'SUCCESS - Prompt is NOT private', then the")
    print("prompt is publicly accessible and not secure.")


if __name__ == "__main__":
    main() 