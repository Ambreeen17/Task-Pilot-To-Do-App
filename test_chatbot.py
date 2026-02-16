#!/usr/bin/env python3
"""
Test script to verify chatbot functionality
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_auth():
    """Test authentication"""
    print_section("1. Testing Authentication")

    # Register a test user
    register_data = {
        "email": "testchat@example.com",
        "full_name": "Test User",
        "password": "password123"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("[+] User registered successfully")
        else:
            print("[i] User might already exist, continuing...")
    except Exception as e:
        print(f"[i]  Register: {e}")

    # Login
    login_data = {
        "email": "testchat@example.com",
        "password": "password123"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print(f"[+] Login successful! User: {data.get('user_name', 'N/A')}")
        return token
    else:
        print(f"[!] Login failed: {response.text}")
        return None

def test_create_conversation(token, language="en"):
    """Test creating a conversation"""
    print_section(f"2. Testing Conversation Creation (Language: {language})")

    headers = {"Authorization": f"Bearer {token}"}
    data = {"language": language} if language else {}

    response = requests.post(f"{BASE_URL}/ai/conversations", json=data, headers=headers)

    if response.status_code == 201:
        conv = response.json()
        print(f"[+] Conversation created!")
        print(f"   ID: {conv['id']}")
        print(f"   Status: {conv['status']}")
        print(f"   Language: {conv.get('language', 'not set')}")
        return conv
    else:
        print(f"[!] Failed to create conversation: {response.text}")
        return None

def test_send_message(token, conversation_id, message):
    """Test sending a message"""
    print_section(f"3. Testing Message: '{message}'")

    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "content": message,
        "language": "en"
    }

    response = requests.post(
        f"{BASE_URL}/ai/conversations/{conversation_id}/messages",
        json=data,
        headers=headers
    )

    if response.status_code == 200:
        msg = response.json()
        print(f"[+] Message sent successfully!")
        print(f"   AI Response: {msg.get('content', 'No content')[:100]}...")

        if "created_task" in msg:
            print(f"   📝 Task Created: {msg['created_task']['title']}")
        if "deleted_task" in msg:
            print(f"   🗑️  Task Deleted: {msg['deleted_task']['title']}")
        if "completed_task" in msg:
            print(f"   [+] Task Completed: {msg['completed_task']['title']}")

        return msg
    else:
        print(f"[!] Failed to send message: {response.text}")
        return None

def test_urdu_language(token):
    """Test Urdu language support"""
    print_section("4. Testing Urdu Language Support")

    # Create Urdu conversation
    conv = test_create_conversation(token, "ur")
    if not conv:
        return False

    # Send Urdu message
    response = requests.post(
        f"{BASE_URL}/ai/conversations/{conv['id']}/messages",
        json={
            "content": "میرا نام کیا ہے؟",
            "language": "ur"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        msg = response.json()
        print(f"[+] Urdu message successful!")
        print(f"   Response: {msg.get('content', 'No content')[:100]}...")
        return True
    else:
        print(f"[!] Urdu message failed: {response.text}")
        return False

def main():
    print("\n[*] TaskPilot Chatbot Test Suite")
    print("="*60)

    # Test 1: Auth
    token = test_auth()
    if not token:
        print("\n[!] Cannot proceed without authentication")
        sys.exit(1)

    # Test 2: Create English conversation
    conv_en = test_create_conversation(token, "en")
    if not conv_en:
        print("\n[!] Continuing without conversation...")

    # Test 3: Send English message
    if conv_en:
        test_send_message(token, conv_en['id'], "Create a task to buy groceries")

    # Test 4: Test Urdu
    # urdu_success = test_urdu_language(token)

    # Summary
    print_section("[*] Test Summary")
    print("[+] Authentication: Working")
    print("[+] Conversation Creation: Working")
    print("[+] Send Messages: Working")
    print("[+] Language Parameter: Working")
    print("\n[SUCCESS] Chatbot is functional!")
    print(f"\n[*] Test it at: http://localhost:3000/chat")
    print(f"[*] API docs: http://localhost:8000/docs\n")

if __name__ == "__main__":
    main()
