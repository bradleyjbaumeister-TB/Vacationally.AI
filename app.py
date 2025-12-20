from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)

# Get Grok API key from environment variable
GROK_API_KEY = os.environ.get('GROK_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-itinerary', methods=['POST'])
def generate_itinerary():
    try:
        data = request.json
        
        # Build the prompt for Grok
        prompt = f"""You are an enthusiastic travel expert helping someone find their perfect vacation destination. Based on their preferences, recommend 3-5 specific destinations that match what they're looking for, then provide a detailed itinerary for the BEST match.

PREFERENCES:
- Vacation Type: {data.get('vacationType', 'Not specified')}
- Travel Method: {data.get('travelMethod', 'Not specified')}
- Budget per person: {data.get('budget', 'Not specified')}
- Traveling with kids: {data.get('hasKids', 'Not specified')}
- Trip Duration: {data.get('tripDuration', 'Not specified')}
- Rental car needed: {data.get('needsCar', 'Not specified')}

FORMAT YOUR RESPONSE LIKE THIS:

🌟 PERFECT DESTINATIONS FOR YOU:

1. [Destination Name] - [Brief reason why it's perfect]
2. [Destination Name] - [Brief reason why it's perfect]
3. [Destination Name] - [Brief reason why it's perfect]

---

📍 TOP PICK: [Best Destination Name]

🎯 WHY YOU'LL LOVE IT:
[2-3 sentences about what makes this destination perfect for them]

✈️ GETTING THERE:
[Flight/driving info, average costs, tips]

🏨 WHERE TO STAY:
[2-3 accommodation recommendations with price ranges]

📅 YOUR ITINERARY:
[Day-by-day breakdown with specific activities, restaurants, and experiences]

🚗 GETTING AROUND:
{'[Detailed public transportation info, apps to download, transit passes to buy, walking areas]' if data.get('needsCar') == 'no' else '[Car rental tips, parking info, driving considerations]'}

💰 BUDGET BREAKDOWN:
[Estimated costs for flights/driving, accommodations, food, activities, transportation]

{'👨‍👩‍👧‍👦 KID-FRIENDLY HIGHLIGHTS: [Specific activities and tips for families]' if data.get('hasKids') == 'yes' else ''}

💡 PRO TIPS:
[3-5 insider tips to make the trip amazing]

Make it exciting, specific, and actionable!"""

        # Call Grok API
        headers = {
            'Authorization': f'Bearer {GROK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        grok_data = {
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'model': 'grok-beta',
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.x.ai/v1/chat/completions',
            headers=headers,
            json=grok_data,
            timeout=30
        )
        
        if response.status_code == 200:
            grok_response = response.json()
            itinerary = grok_response['choices'][0]['message']['content']
            return jsonify({
                'success': True,
                'itinerary': itinerary
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Grok API error: {response.status_code}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
