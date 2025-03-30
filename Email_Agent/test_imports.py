#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
This helps identify dependency issues before deployment.
"""

import sys
print("Python version:", sys.version)

# Test all imports used in the application
print("\nTesting Flask imports...")
import flask
from flask import Flask, request, jsonify, send_file
print("✅ Flask imports successful")

print("\nTesting basic libraries...")
import os
import io
import csv
import json
import smtplib
import tempfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import dateutil
from dateutil.parser import parse
print("✅ Basic libraries imports successful")

print("\nTesting Werkzeug...")
import werkzeug
print("Werkzeug version:", werkzeug.__version__)
print("✅ Werkzeug import successful")

print("\nTesting numpy...")
import numpy as np
print("NumPy version:", np.__version__)
print("✅ NumPy import successful")

print("\nTesting dotenv...")
import dotenv
from dotenv import load_dotenv
print("✅ Dotenv imports successful")

print("\nTesting Google API libraries...")
import google.auth
import google_auth_httplib2
import googleapiclient
from googleapiclient.discovery import build
print("✅ Google API imports successful")

print("\nTesting LangChain imports...")
import openai
print("OpenAI version:", openai.__version__)
import langchain
print("LangChain version:", langchain.__version__)
try:
    import langchain_openai
    from langchain_openai import ChatOpenAI
    print("LangChain OpenAI version:", langchain_openai.__version__)
    print("✅ LangChain OpenAI imports successful")
except Exception as e:
    print("❌ Error importing langchain_openai:", str(e))

try:
    import langchain_core
    print("LangChain Core version:", langchain_core.__version__)
    print("✅ LangChain Core imports successful")
except Exception as e:
    print("❌ Error importing langchain_core:", str(e))

print("\nTesting other dependencies...")
import requests
import aiohttp
import bs4
from bs4 import BeautifulSoup
import markdown
from slugify import slugify
try:
    import google.cloud.storage
    print("✅ Google Cloud Storage import successful")
except Exception as e:
    print("❌ Error importing google.cloud.storage:", str(e))

print("\nAll import tests completed!")
