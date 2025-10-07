"""
Test Redis connection from Python.
Run with: python test_redis.py
"""
import redis
import sys

def test_redis():
    """Test Redis connection and basic operations."""
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        # Test ping
        if not r.ping():
            print("ERROR: Redis ping failed")
            sys.exit(1)

        # Test set/get
        test_key = "onlsuggest:test"
        test_value = "Hello Redis!"
        r.set(test_key, test_value, ex=10)  # Expires in 10 seconds

        retrieved_value = r.get(test_key)

        if retrieved_value == test_value:
            print(f"✓ Redis test: {retrieved_value}")
            r.delete(test_key)  # Clean up
            sys.exit(0)
        else:
            print(f"ERROR: Expected '{test_value}', got '{retrieved_value}'")
            sys.exit(1)

    except redis.ConnectionError as e:
        print(f"ERROR: Could not connect to Redis: {e}")
        print("Make sure Redis is running on localhost:6379")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_redis()
