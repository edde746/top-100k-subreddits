import requests,os,time,json
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

auth = requests.post('https://www.reddit.com/api/v1/access_token', headers={
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': os.getenv('USER_AGENT'),
}, auth=(os.getenv('REDDIT_CLIENT_ID'), os.getenv('REDDIT_SECRET')), data={
    'grant_type': 'password',
    'username': os.getenv('REDDIT_USERNAME'),
    'password': os.getenv('REDDIT_PASSWORD'),
}).json()

if not auth.get('access_token'):
    print('Authentication failed', auth)
    raise Exception('Reddit authentication failed')

filename = f'subreddits-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.json'

after = ''
subreddits = []
while True:
    res = requests.get(f'https://oauth.reddit.com/subreddits/popular.json?limit=100&after={after}', headers={
        'Authorization': f'Bearer {auth["access_token"]}',
        'User-Agent': os.getenv('USER_AGENT'),
    })
    
    if res.status_code != 200:
        time.sleep(10)
        continue

    res = res.json()
    subreddits += [subreddit['data'] for subreddit in res['data']['children']]
    # save to file
    with open(filename, 'w') as f:
        f.write(json.dumps(subreddits))

    after = res['data']['after']
    print(f'Got {len(subreddits)} subreddits')

    if len(subreddits) >= 100_000 or len(res['data']['children']) < 50:
        break

