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
        prompt = f"""You are an enthusiastic travel expert helping someone discover their perfect vacation destination. Based on their detailed preferences, recommend 3-5 specific destinations that perfectly match their personality and travel style, then provide a comprehensive itinerary for the BEST match.

TRAVELER PROFILE:
- Weather Preference: {data.get('weather', 'Not specified')}
- Activity Level: {data.get('activityLevel', 'Not specified')}
- Crowd Tolerance: {data.get('crowds', 'Not specified')}
- Food Interest: {data.get('food', 'Not specified')}
- Cultural Interest: {data.get('culture', 'Not specified')}
- Nightlife Preference: {data.get('nightlife', 'Not specified')}
- Setting Preference: {data.get('setting', 'Not specified')}
- Travel Style: {data.get('travelStyle', 'Not specified')}
- Travel Method: {data.get('travelMethod', 'Not specified')}
- Total Trip Budget: ${data.get('totalBudget', 'Not specified')}
- Number of Children: {data.get('numKids', 'Not specified')}
- Trip Duration: {data.get('tripDuration', 'Not specified')}
- Rental Car: {data.get('needsCar', 'Not specified')}

CRITICAL: All destination recommendations MUST fit within their ${data.get('totalBudget', 'Not specified')} budget AND match their preferences perfectly.

FORMAT YOUR RESPONSE LIKE THIS:

🎯 BASED ON YOUR PREFERENCES, HERE ARE YOUR PERFECT MATCHES:

1. [Destination Name] - Est. Cost: $[amount]
   Why it's perfect: [Explain how it matches their weather, activity level, crowd preference, food scene, culture, nightlife, and setting preferences]

2. [Destination Name] - Est. Cost: $[amount]
   Why it's perfect: [Match to their specific preferences]

3. [Destination Name] - Est. Cost: $[amount]
   Why it's perfect: [Match to their specific preferences]

---

📍 YOUR #1 MATCH: [Best Destination Name]
💰 ESTIMATED TOTAL COST: $[amount] (within your ${data.get('totalBudget', 'Not specified')} budget)

🎯 WHY THIS IS YOUR PERFECT DESTINATION:
[Detailed explanation of how this destination matches their weather preference, activity level, crowd tolerance, food interests, cultural interests, nightlife preference, and setting preference. Be specific about why this beats the other options for THEM.]

✈️ GETTING THERE:
{f"[Flight options, airlines, booking tips, estimated costs based on their travel style: {data.get('travelStyle', 'Not specified')}]" if data.get('travelMethod') in ['fly', 'either'] else f"[Driving route, road trip highlights, estimated gas costs, recommended stops, travel time]"}

🏨 WHERE TO STAY - MATCHED TO YOUR STYLE:
[2-3 accommodation recommendations that match their {data.get('travelStyle', 'Not specified')} travel style, with nightly rates and why each fits their preferences]

📅 YOUR PERSONALIZED ITINERARY:
[Create a day-by-day breakdown that reflects their activity level ({data.get('activityLevel', 'Not specified')}), food interests ({data.get('food', 'Not specified')}), cultural interests ({data.get('culture', 'Not specified')}), and nightlife preferences ({data.get('nightlife', 'Not specified')}). Include specific restaurants, activities, and experiences.]

🚗 GETTING AROUND:
{f"[Public transportation details, walkability, transit apps, passes to buy, estimated costs] - Perfect for someone who prefers {data.get('crowds', 'Not specified')} crowds" if data.get('needsCar') == 'no' else f"[Car rental recommendations, parking tips, driving considerations, estimated costs] - Great for exploring at your own pace" if data.get('needsCar') == 'yes' else "[Transportation recommendations based on your destination - I'll tell you whether a car makes sense or not]"}

💰 DETAILED BUDGET BREAKDOWN:
- Transportation: $[amount]
- Accommodations ([X] nights at {data.get('travelStyle', 'Not specified')} level): $[amount]
- Food & Dining (matching {data.get('food', 'Not specified')} preferences): $[amount]
- Activities & Entertainment: $[amount]
- Local Transportation: $[amount]
- Miscellaneous: $[amount]
**TOTAL: $[amount]** ✓ Within budget

{'👨‍👩‍👧‍👦 TRAVELING WITH ' + data.get('numKids', '0') + ' KIDS: [Age-appropriate activities, kid-friendly restaurants that match your food preferences, family logistics, childcare options if parents want a night out based on nightlife preference]' if data.get('numKids', '0') != '0' else ''}

🌤️ WEATHER & WHAT TO PACK:
[Expected weather conditions that match their preference for {data.get('weather', 'Not specified')}, packing list, best time to visit]

💡 INSIDER TIPS FOR YOUR TRAVEL STYLE:
[5-7 specific tips that match their preferences for crowds ({data.get('crowds', 'Not specified')}), activity level ({data.get('activityLevel', 'Not specified')}), and budget ({data.get('travelStyle', 'Not specified')})]

Make it feel like you deeply understand them as a traveler and this destination was chosen specifically for their unique combination of preferences!"""

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
    
