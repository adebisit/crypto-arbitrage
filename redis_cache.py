import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_value(key):
    return redis_client.get(key)

def set_value(key, value):
    return redis_client.set(key, value)