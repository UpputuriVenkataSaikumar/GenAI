from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Citations Checker</title>
    </head>
    <body>
        <h1>Citations Checker</h1>
        <form id="apiForm">
            <label for="apiUrl">API URL:</label><br>
            <input type="text" id="apiUrl" name="apiUrl" required><br><br>
            <label for="responseText">Response Text:</label><br>
            <textarea id="responseText" name="responseText" rows="10" cols="50" required></textarea><br><br>
            <button type="submit">Check Citations</button>
        </form>
        <h2>Citations:</h2>
        <ul id="citationsList"></ul>
        <script>
            document.getElementById('apiForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const apiUrl = document.getElementById('apiUrl').value;
                const responseText = document.getElementById('responseText').value;
                const response = await fetch('/api/citations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ apiUrl, responseText })
                });
                const citations = await response.json();
                const list = document.getElementById('citationsList');
                list.innerHTML = '';
                citations.forEach(citation => {
                    const li = document.createElement('li');
                    li.textContent = `ID: ${citation.id}, Link: ${citation.link}`;
                    list.appendChild(li);
                });
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/api/citations', methods=['POST'])
def get_citations():
    data = request.get_json()
    api_url = data.get('apiUrl')
    response_text = data.get('responseText')
    api_data = fetch_data_from_api(api_url)
    citations = find_citations(api_data, response_text)
    return jsonify(citations)

def fetch_data_from_api(api_url: str):
    data = []
    page = 1
    while True:
        response = requests.get(f"{api_url}?page={page}")
        if response.status_code != 200:
            break
        page_data = response.json()
        if not page_data:
            break
        data.extend(page_data)
        page += 1
    return data

def find_citations(data, response_text):
    citations = []
    for item in data:
        sources = item.get('sources', [])
        citation = []
        for source in sources:
            if source['context'] in response_text:
                citation.append({'id': source['id'], 'link': source.get('link', '')})
        if citation:
            citations.extend(citation)
    return citations

if __name__ == '__main__':
    app.run(debug=True)
