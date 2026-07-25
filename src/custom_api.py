from berserk import Client

def get_my_timeline(client:Client) -> dict:
    return client._r.get('/api/timeline')