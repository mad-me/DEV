#!/usr/bin/env python3
"""
Zeigt Bolt API JSON-Daten an
"""

import json
from bolt_api_correct import BoltAPICorrect
from datetime import datetime, timedelta

def show_json_data():
    api = BoltAPICorrect()
    
    print("🔍 Bolt API JSON-Daten Anzeige")
    print("=" * 40)
    
    # Hole Reports-Daten
    print("\n📊 Reports-Daten:")
    print("-" * 30)
    reports_data = api.get_reports_data()
    if reports_data:
        print(json.dumps(reports_data, indent=2, ensure_ascii=False))
    
    print("\n" + "="*50)
    
    # Hole Dashboard-Daten
    print("\n📊 Dashboard-Daten:")
    print("-" * 30)
    dashboard_data = api.get_dashboard_data()
    if dashboard_data:
        print(json.dumps(dashboard_data, indent=2, ensure_ascii=False))
    
    print("\n" + "="*50)
    
    # Hole Performance-Daten
    print("\n📊 Performance-Daten:")
    print("-" * 30)
    performance_data = api.get_performance_data()
    if performance_data:
        print(json.dumps(performance_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    show_json_data() 