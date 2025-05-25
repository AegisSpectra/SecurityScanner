import requests

API_KEY = "YOUR_VIRUSTOTAL_API_KEY"  # Replace with your actual key

def check_hash_virustotal(hash_value):
    url = f"https://www.virustotal.com/api/v3/files/{hash_value}"
    headers = {"x-apikey": API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        stats = data["data"]["attributes"]["last_analysis_stats"]
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        harmless = stats.get("harmless", 0)
        return f"[VT] Malicious: {malicious} | Suspicious: {suspicious} | Harmless: {harmless}"
    elif response.status_code == 404:
        return "[VT] Not found in VirusTotal database"
    else:
        return f"[VT] Error: {response.status_code}"