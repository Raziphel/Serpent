import redis
import toml

class RedisUtils:
    def __init__(self, config_path='secret.toml'):
        config = toml.load(config_path)['redis']
        self.redis = redis.Redis(
            host=config.get('host', 'localhost'),
            port=config.get('port', 6379),
            password=config.get('password', None),
            db=config.get('db', 0),
            decode_responses=True
        )

    def is_connected(self):
        try:
            return self.redis.ping()
        except redis.ConnectionError:
            return False

    def publish(self, channel, message):
        try:
            self.redis.publish(channel, message)
            return True
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return False

    def subscribe(self, channel):
        try:
            pubsub = self.redis.pubsub()
            pubsub.subscribe(channel)
            return pubsub
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return None

    def get_value(self, key):
        try:
            return self.redis.get(key)
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return None

    def set_value(self, key, value):
        try:
            self.redis.set(key, value)
        except redis.RedisError as e:
            print(f"Redis error: {e}")
