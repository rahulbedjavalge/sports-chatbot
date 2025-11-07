# Performance Optimization and Caching Implementation
import time
import json
import hashlib
from functools import wraps
from datetime import datetime, timedelta

class ResponseCache:
    """Simple in-memory cache for API responses"""
    
    def __init__(self, max_size=1000, ttl_seconds=3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.access_times = {}
    
    def _generate_key(self, text, intent=None):
        """Generate cache key from input"""
        key_data = f"{text.lower().strip()}{intent or ''}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, text, intent=None):
        """Get cached response"""
        key = self._generate_key(text, intent)
        
        if key in self.cache:
            cached_item = self.cache[key]
            
            # Check if expired
            if datetime.now() - cached_item['timestamp'] < timedelta(seconds=self.ttl_seconds):
                self.access_times[key] = datetime.now()
                print(f"💾 Cache HIT for: {text[:30]}...")
                return cached_item['response']
            else:
                # Expired
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
        
        print(f"💾 Cache MISS for: {text[:30]}...")
        return None
    
    def set(self, text, response, intent=None):
        """Cache response"""
        key = self._generate_key(text, intent)
        
        # Implement LRU eviction if cache is full
        if len(self.cache) >= self.max_size:
            # Remove oldest accessed item
            oldest_key = min(self.access_times.keys(), 
                           key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = {
            'response': response,
            'timestamp': datetime.now()
        }
        self.access_times[key] = datetime.now()
        print(f"💾 Cached response for: {text[:30]}...")
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.access_times.clear()
        print("💾 Cache cleared")
    
    def stats(self):
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds
        }

# Global cache instances
response_cache = ResponseCache(max_size=500, ttl_seconds=1800)  # 30 minutes
model_cache = ResponseCache(max_size=200, ttl_seconds=3600)     # 1 hour

def cache_response(cache_type='response'):
    """Decorator to cache function responses"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use the first argument (usually text) as cache key
            if args:
                cache_key = str(args[0])
                selected_cache = response_cache if cache_type == 'response' else model_cache
                
                # Try to get from cache
                cached_result = selected_cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                selected_cache.set(cache_key, result)
                return result
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

class PerformanceMonitor:
    """Monitor API performance and response times"""
    
    def __init__(self):
        self.request_times = []
        self.intent_accuracy = []
        self.response_methods = {'structured': 0, 'llm': 0}
    
    def log_request(self, duration, intent, confidence, method):
        """Log request performance metrics"""
        self.request_times.append({
            'duration': duration,
            'timestamp': datetime.now(),
            'intent': intent,
            'confidence': confidence,
            'method': method
        })
        
        self.response_methods[method] = self.response_methods.get(method, 0) + 1
        
        # Keep only last 1000 requests
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
    
    def get_stats(self):
        """Get performance statistics"""
        if not self.request_times:
            return {"message": "No requests logged yet"}
        
        recent_times = [r['duration'] for r in self.request_times[-100:]]
        
        return {
            'total_requests': len(self.request_times),
            'avg_response_time': sum(recent_times) / len(recent_times),
            'min_response_time': min(recent_times),
            'max_response_time': max(recent_times),
            'response_methods': self.response_methods,
            'cache_stats': response_cache.stats()
        }

# Global performance monitor
perf_monitor = PerformanceMonitor()

def timed_request(func):
    """Decorator to time API requests"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        # Extract performance data from result if it's a JSON response
        try:
            if hasattr(result, 'get_json'):
                data = result.get_json()
                if data:
                    intent = data.get('intent', 'unknown')
                    confidence = data.get('confidence', 0)
                    method = data.get('method', 'unknown')
                    perf_monitor.log_request(duration, intent, confidence, method)
        except:
            pass
        
        print(f"⏱️ Request took {duration:.3f}s")
        return result
    return wrapper

# Database query optimization
class QueryOptimizer:
    """Optimize database queries with indexing suggestions"""
    
    @staticmethod
    def suggest_indexes():
        """Suggest database indexes for better performance"""
        suggestions = [
            "CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(home_team_id, away_team_id);",
            "CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);",
            "CREATE INDEX IF NOT EXISTS idx_players_team ON players(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);",
            "CREATE INDEX IF NOT EXISTS idx_scorers_match ON scorers(match_id);",
            "CREATE INDEX IF NOT EXISTS idx_scorers_player ON scorers(player_id);",
            "CREATE INDEX IF NOT EXISTS idx_standings_team ON team_standings(team_id);",
            "CREATE INDEX IF NOT EXISTS idx_standings_tournament ON team_standings(tournament_id);"
        ]
        return suggestions
    
    @staticmethod
    def apply_indexes(db_path):
        """Apply suggested indexes to database"""
        import sqlite3
        
        suggestions = QueryOptimizer.suggest_indexes()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            for index_sql in suggestions:
                try:
                    cursor.execute(index_sql)
                    print(f"✅ Applied: {index_sql}")
                except Exception as e:
                    print(f"⚠️ Could not apply: {index_sql} - {e}")
            
            conn.commit()
            conn.close()
            print("🚀 Database optimization completed!")
            
        except Exception as e:
            print(f"❌ Database optimization failed: {e}")

if __name__ == "__main__":
    print("🔧 Performance Optimization Module")
    print("📊 Cache configuration:")
    print(f"  - Response cache: {response_cache.max_size} items, {response_cache.ttl_seconds}s TTL")
    print(f"  - Model cache: {model_cache.max_size} items, {model_cache.ttl_seconds}s TTL")
    
    print("\n🗃️ Applying database indexes...")
    QueryOptimizer.apply_indexes("db.sqlite3")