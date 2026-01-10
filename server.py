# server.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)  # Allows your HTML file to talk to this Python server

def scrape_myneta(search_name):
    """
    Scrapes myneta.info. 
    NOTE: Since myneta search is complex, for this prototype we will 
    search Google to find the specific myneta URL for the candidate.
    """
    try:
        # 1. Search Logic (Simulated for specific real politicians for demo)
        # In a production app, you would use the 'googlesearch-python' library here.
        # For this prototype, let's Map names to specific MyNeta URLs to ensure it works for you instantly.
        
        # Example URLs (You can add more real URLs here)
        urls = {
            "hema malini": "https://myneta.info/LokSabha2024/candidate.php?candidate_id=5676",
            "yogi adityanath": "https://myneta.info/uttarpradesh2022/candidate.php?candidate_id=6486",
            "akhilesh yadav": "https://myneta.info/uttarpradesh2022/candidate.php?candidate_id=6487"
        }
        
        target_url = urls.get(search_name.lower())
        
        if not target_url:
            return {"error": "Politician not found in demo database."}

        # 2. Fetch the Page
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 3. Extract Data (Parsing the HTML structure of MyNeta)
        data = {}
        
        # A. Get Name
        name_tag = soup.find('h2', class_='main-title')
        data['name'] = name_tag.text.strip() if name_tag else search_name

        # B. Get Criminal Cases
        # MyNeta usually lists this in a specific red text or bold format
        criminal_text = soup.find(text=re.compile(r'Criminal Case'))
        if criminal_text:
            # Look for the number usually following the text
            parent = criminal_text.parent
            data['criminal_cases'] = parent.find_next('span').text.strip()
        else:
            data['criminal_cases'] = "0"

        # C. Get Assets
        assets_text = soup.find(text=re.compile(r'Total Assets'))
        if assets_text:
            parent_row = assets_text.find_parent('tr')
            if parent_row:
                # The amount is usually in the last column of that row
                amount = parent_row.find_all('td')[-1].text.strip()
                data['assets'] = amount
        
        # D. Education
        edu_text = soup.find(text=re.compile(r'Education Detail'))
        if edu_text:
             # Logic to find the specific education degree nearby
             # Simplified: just return "Available in full profile" or scrape the specific div
             data['education'] = "Detailed on Source"

        data['source_url'] = target_url
        return data

    except Exception as e:
        return {"error": str(e)}

@app.route('/api/leader-details', methods=['GET'])
def get_leader_details():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    result = scrape_myneta(name)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

