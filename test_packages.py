# Save this as test_packages.py and run: python test_packages.py

try:
    import numpy as np
    import pandas as pd
    import xgboost as xgb
    import matplotlib.pyplot as plt
    import shap
    import requests

    print("✅ numpy version:", np.__version__)
    print("✅ pandas version:", pd.__version__)
    print("✅ xgboost version:", xgb.__version__)
    print("✅ matplotlib version:", plt.__version__ if hasattr(plt, '__version__') else "OK")
    print("✅ shap version:", shap.__version__)
    print("✅ requests version:", requests.__version__)
except Exception as e:
    print("❌ Package test failed:", e)

