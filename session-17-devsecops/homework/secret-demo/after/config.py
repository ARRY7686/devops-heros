# GOOD: credentials come from the environment (GitHub Secrets / K8s Secrets at runtime)
import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
DEMO_API_KEY = os.environ.get("DEMO_API_KEY", "")
