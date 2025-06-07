#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

BF_USERNAME = os.getenv("BF_USERNAME")
BF_PASSWORD = os.getenv("BF_PASSWORD")
BF_APP_KEY = os.getenv("BF_APP_KEY")
BF_CERT_PATH = os.getenv("BF_CERT_PATH")
BF_KEY_PATH = os.getenv("BF_KEY_PATH")
BF_CERT_DIR = os.getenv("BF_CERT_DIR")
