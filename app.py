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
        prompt = f"""You are an enthusiastic travel expert helping someone find their perfect vacation destination. Based on their preferences and budget, recommend 3-5 specific destinations that fit WITHIN their budget, then provide a detailed itinerary for the BEST match.

PREFERENCES:
- Vacation Type: {data.get('vacationType', 'Not specified')}
- Travel Method: {data.get('travelMethod', 'Not specified')}
- Total Trip Budget: ${data.get('totalBudget', 'Not specified')}
- Number of Children: {data.get('numKids', 'Not specified')}
- Trip Duration: {data.get('tripDuration', 'Not specified')}
- Rental car needed: {data.get('needsCar', 'Not specified')}

CRITICAL: All destination recommendations MUST fit within their ${data.get('totalBudget', 'Not specified')} budget. Include realistic cost estimates.

FORMAT YOUR RESPONSE LIKE THIS:

🌟 DESTINATIONS WITHIN YOUR ${data.get('totalBudget', 'Not specified')} BUDGET:

1. [Destination Name] - Estimated Total: $[amount] - [Brief reason why it's perfect]
2. [Destination Name] - Estimated Total: $[amount] - [Brief reason why it's perfect]
3. [Destination Name] - Estimated Total: $[amount] - [Brief reason why it's perfect]

---

📍 TOP PICK: [Best Destination Name]
💰 ESTIMATED TOTAL COST: $[amount]

🎯 WHY YOU'LL LOVE IT:
[2-3 sentences about what makes this destination perfect for them]

✈️ GETTING THERE:
[Flight/driving info, realistic costs based on their travel method]

🏨 WHERE TO STAY:
[2-3 accommodation recommendations within budget, with nightly rates]

📅 YOUR ITINERARY:
[Day-by-day breakdown with specific activities, restaurants, and experiences - all within budget]

🚗 GETTING AROUND:
{'[Detailed public transportation info, apps to download, transit passes to buy, walking areas, costs]' if data.get('needsCar') == 'no' else '[Car rental tips, estimated daily rate, parking info, driving considerations, gas costs]'}

💰 DETAILED BUDGET BREAKDOWN:
- Transportation (flights/gas/car rental): $[amount]
- Accommodations ([X] nights): $[amount]
- Food & Dining: $[amount]
- Activities & Entertainment: $[amount]
- Local Transportation: $[amount]
- Miscellaneous/Contingency: $[amount]
**TOTAL: $[amount]** (within ${data.get('totalBudget', 'Not specified')} budget)

{'👨‍👩‍👧‍👦 FAMILY TIPS WITH ' + data.get('numKids', '0') + ' KIDS: [Specific activities, kid-friendly restaurants, and family travel tips]' if data.get('numKids', '0') != '0' else ''}

💡 MONEY-SAVING TIPS:
[3-5 specific ways to save money on this trip]

Make it exciting, specific, realistic, and ensure everything fits their budget!"""

        # Call Grok API
        headers = {
            'Authorization': f'Bearer {GROK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        grok_data = {
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a helpful travel assistant.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'model': 'grok-beta',
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
            return jsonify({
                'success': True,
                'itinerary': itinerary
            })
        else:
            error_detail = response.text
            print(f"Grok API Error {response.status_code}: {error_detail}")
            return jsonify({
                'success': False,
                'error': f'Grok API error: {response.status_code}. Details: {error_detail}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
