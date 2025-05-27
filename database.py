import logging
import json
import redis

logger = logging.getLogger(__name__)


class Database: 
    """
    Redis Persistent Database that maintains the most recent status information
    """
    def __init__(self, redis_url):
        self.db = redis.from_url(redis_url, decode_responses=True)
        logger.info(f"The REDIS database has been set up")

    def get_recent(self, id): 
        key = f"Client{id}"
        value = self.db.hgetall(key)
        return value

    def update_recent(self, id, decision, curr_time, status):
        key = f"Client{id}"
        self.db.hset(key, mapping={
            "decision": decision,
            "time_stamp": curr_time,
            "geojson": json.dumps(status),
        })