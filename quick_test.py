import requests
import json

payload = {
    "user_request": "Create a vibrant tropical drink advertisement featuring a large watermelon juice bottle in the center. The bottle should appear big, glossy, and labeled 'WATERMELON JUICE – SUMMER FRESH.' Place a glass of watermelon juice beside it. Surround the bottle with watermelon slices, cubes, and whole mini watermelons floating around. Add a splash of red juice splattering around the bottle. The background should include a sunny tropical beach or palm trees, with blue sky and bright light rays. Include ice cubes, water droplets, and sparkles to give a fresh, lively effect."
}

print("🍉 Testing Watermelon Juice Advertisement...")
response = requests.post('http://localhost:8000/api/v1/extract-and-fill', json=payload)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print("✅ Extraction successful!")
    print(f"📊 Extracted fields: {len(data)} fields")
    print("\n🎯 Sample fields:")
    for i, (key, value) in enumerate(list(data.items())[:3]):
        print(f"  {key}: {value}")
else:
    print(f"❌ Error: {response.text}")
