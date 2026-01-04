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
        
        prompt = f"""You are an enthusiastic travel expert. Based on these preferences, recommend 3-5 destinations within budget and provide a detailed itinerary for the best match.

TRAVELER PROFILE:
- Weather: {data.get('weather')}
- Activity Level: {data.get('activityLevel')}
- Crowds: {data.get('crowds')}
- Food: {data.get('food')}
- Culture: {data.get('culture')}
- Nightlife: {data.get('nightlife')}
- Setting: {data.get('setting')}
- Travel Style: {data.get('travelStyle')}
- Travel Method: {data.get('travelMethod')}
- Budget: ${data.get('totalBudget')}
- Children: {data.get('numKids')}
- Duration: {data.get('tripDuration')}
- Car Rental: {data.get('needsCar')}

Provide: destination options with costs, detailed itinerary, accommodations, transportation, budget breakdown, and personalized tips."""

        headers = {
            'Authorization': f'Bearer {GROK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        grok_data = {
            'messages': [
                {'role': 'system', 'content': 'You are a helpful travel assistant.'},
                {'role': 'user', 'content': prompt}
            ],
            'model': 'grok-2-vision-1212',
            'stream': False,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.x.ai/v1/chat/completions',
            headers=headers,
            json=grok_data,
            timeout=60
        )
        
        if response.status_code == 200:
            grok_response = response.json()
            itinerary = grok_response['choices'][0]['message']['content']
            return jsonify({'success': True, 'itinerary': itinerary})
        else:
            error_detail = response.text
            return jsonify({'success': False, 'error': f'API error: {response.status_code}. {error_detail}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
