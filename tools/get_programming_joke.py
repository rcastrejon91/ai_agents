def get_programming_joke(**kwargs):
    import requests
    import json
    try:
        response = requests.get('https://v2.jokeapi.dev/joke/Programming')
        data = response.json()
        if data['type'] == 'twopart':
            joke = data['setup'] + ' ' + data['delivery']
        else:
            joke = data['joke']
        return {"result": joke}
    except Exception as e:
        return {"error": str(e)}