import os
from dotenv import load_dotenv

load_dotenv()

BF_USERNAME = os.environ.get("BF_USERNAME")
BF_PASSWORD = os.environ.get("BF_PASSWORD")
BF_APP_KEY = os.environ.get("BF_APP_KEY")
BF_CERT_PATH = os.environ.get("BF_CERT_PATH")
BF_KEY_PATH = os.environ.get("BF_KEY_PATH")
# BF_CERT_DIR has been removed as paths are expected to be absolute.
# It can be made configurable if needed:
# BF_CERT_DIR = os.environ.get("BF_CERT_DIR", os.path.dirname(os.environ.get("BF_CERT_PATH", "")))
