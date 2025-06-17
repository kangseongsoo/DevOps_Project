import redis
import json
from datetime import datetime

def test_redis():
    """Redis 연결과 기본 기능 테스트"""
    try:
        # Redis 연결
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print('✅ Redis 연결 성공!')
        
        # 테스트 데이터 저장
        test_data = {
            'role': 'user',
            'content': '안녕하세요! Redis 테스트입니다.',
            'timestamp': datetime.now().isoformat()
        }
        
        r.lpush('test:conversation', json.dumps(test_data))
        print('✅ Redis에 데이터 저장 성공!')
        
        # 데이터 조회
        stored_data = r.lrange('test:conversation', 0, -1)
        print(f'📦 저장된 데이터: {stored_data}')
        
        # 정리
        r.delete('test:conversation')
        print('🧹 테스트 데이터 정리 완료!')
        
        return True
        
    except Exception as e:
        print(f'❌ Redis 연결 실패: {e}')
        return False

if __name__ == "__main__":
    test_redis() 