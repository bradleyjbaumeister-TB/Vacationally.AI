from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)

GROK_API_KEY = os.environ.get('GROK_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-itinerary', methods=['POST'])
def generate_itinerary():
    try:
        data = request.json
        
        prompt = f"""You are an enthusiastic travel expert. Recommend 3-5 destinations within ${data.get('totalBudget')} budget.
Preferences: {data.get('weather')}, {data.get('activityLevel')}, {data.get('crowds')}, {data.get('food')}, 
{data.get('culture')}, {data.get('nightlife')}, {data.get('setting')}, {data.get('travelStyle')}, 
{data.get('travelMethod')}, {data.get('numKids')} kids, {data.get('tripDuration')}, car: {data.get('needsCar')}.
Provide detailed itinerary with costs, accommodations, transportation, and tips."""

        response = requests.post(
            'https://api.x.ai/v1/chat/completions',
            headers={'Authorization': f'Bearer {GROK_API_KEY}', 'Content-Type': 'application/json'},
            json={
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful travel assistant.'},
                    {'role': 'user', 'content': prompt}
                ],
                'model': 'grok-2-vision-1212',
                'stream': False,
                'temperature': 0.7
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return jsonify({'success': True, 'itinerary': response.json()['choices'][0]['message']['content']})
        else:
            return jsonify({'success': False, 'error': f'API error {response.status_code}: {response.text}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
