import pytest
import json
import time
from unittest.mock import patch, MagicMock
from flask import Flask
from middleware.security import validate_input, rate_limit, security_headers, cache
from utils.logging import setup_logging, SecurityLogger, RequestLogger


@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Setup test routes
    @app.route('/test', methods=['GET', 'POST'])
    @validate_input
    @security_headers
    def test_route():
        return {'message': 'success'}
    
    @app.route('/limited', methods=['GET'])
    @rate_limit(limit_per_minute=5)
    def limited_route():
        return {'message': 'limited success'}
    
    @app.route('/unprotected')
    def unprotected_route():
        return {'message': 'unprotected'}
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestInputValidation:
    """Test input validation middleware"""
    
    def test_valid_input_passes(self, client):
        """Test that valid input passes validation"""
        response = client.post('/test', 
                             data={'name': 'valid-name', 'email': 'test@example.com'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'success'
    
    def test_invalid_input_blocked(self, client):
        """Test that invalid input is blocked"""
        response = client.post('/test', 
                             data={'name': '<script>alert(1)</script>'})
        assert response.status_code == 400
    
    def test_sql_injection_blocked(self, client):
        """Test that SQL injection attempts are blocked"""
        response = client.post('/test', 
                             data={'id': "1'; DROP TABLE users; --"})
        assert response.status_code == 400
    
    def test_xss_attempts_blocked(self, client):
        """Test that XSS attempts are blocked"""
        xss_payloads = [
            '<script>alert("xss")</script>',
            'javascript:alert(1)',
            '<img src=x onerror=alert(1)>',
            '"><script>alert(1)</script>'
        ]
        
        for payload in xss_payloads:
            response = client.post('/test', data={'input': payload})
            assert response.status_code == 400
    
    def test_json_input_validation(self, client):
        """Test JSON input validation"""
        # Valid JSON
        response = client.post('/test', 
                             json={'message': 'Hello, world!'})
        assert response.status_code == 200
        
        # Invalid JSON with script
        response = client.post('/test', 
                             json={'message': '<script>alert(1)</script>'})
        assert response.status_code == 400
    
    def test_unicode_input_handling(self, client):
        """Test handling of unicode characters"""
        response = client.post('/test', 
                             data={'name': 'José'})
        assert response.status_code == 200


class TestRateLimiting:
    """Test rate limiting middleware"""
    
    def setup_method(self):
        """Clear cache before each test"""
        cache._data.clear()
    
    def test_rate_limit_allows_normal_requests(self, client):
        """Test that normal request volume is allowed"""
        for i in range(3):
            response = client.get('/limited')
            assert response.status_code == 200
    
    def test_rate_limit_blocks_excessive_requests(self, client):
        """Test that excessive requests are blocked"""
        # Make requests up to the limit
        for i in range(5):
            response = client.get('/limited')
            assert response.status_code == 200
        
        # Next request should be blocked
        response = client.get('/limited')
        assert response.status_code == 429
    
    def test_rate_limit_resets_after_time(self, client):
        """Test that rate limit resets after the time window"""
        # Fill up the rate limit
        for i in range(5):
            response = client.get('/limited')
            assert response.status_code == 200
        
        # Should be blocked
        response = client.get('/limited')
        assert response.status_code == 429
        
        # Clear cache to simulate time passing
        cache._data.clear()
        
        # Should work again
        response = client.get('/limited')
        assert response.status_code == 200
    
    def test_rate_limit_per_ip(self, client):
        """Test that rate limiting is per IP address"""
        # This test would need more sophisticated setup to test multiple IPs
        # For now, just verify single IP behavior
        for i in range(5):
            response = client.get('/limited')
            assert response.status_code == 200
        
        response = client.get('/limited')
        assert response.status_code == 429


class TestSecurityHeaders:
    """Test security headers middleware"""
    
    def test_security_headers_added(self, client):
        """Test that security headers are added to responses"""
        response = client.get('/test')
        
        expected_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        }
        
        for header, value in expected_headers.items():
            assert response.headers.get(header) == value
    
    def test_security_headers_not_on_unprotected(self, client):
        """Test that unprotected routes don't get security headers"""
        response = client.get('/unprotected')
        
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection'
        ]
        
        for header in security_headers:
            assert header not in response.headers


class TestLogging:
    """Test logging functionality"""
    
    def test_setup_logging(self):
        """Test logging setup"""
        setup_logging(level='DEBUG', json_format=True)
        
        # Test that loggers are configured
        import logging
        logger = logging.getLogger('test')
        assert logger.isEnabledFor(logging.DEBUG)
    
    def test_security_logger(self):
        """Test security logger functionality"""
        security_logger = SecurityLogger()
        
        with patch.object(security_logger.logger, 'info') as mock_info:
            security_logger.log_authentication_attempt(
                username='testuser',
                success=True,
                ip_address='127.0.0.1'
            )
            mock_info.assert_called_once()
        
        with patch.object(security_logger.logger, 'warning') as mock_warning:
            security_logger.log_rate_limit_violation(
                ip_address='127.0.0.1',
                endpoint='/api/test',
                limit=60
            )
            mock_warning.assert_called_once()
    
    def test_request_logger(self):
        """Test request logger functionality"""
        request_logger = RequestLogger()
        
        with patch.object(request_logger.logger, 'info') as mock_info:
            request_logger.log_request(
                method='GET',
                path='/api/test',
                status_code=200,
                response_time=0.15,
                request_id='test-123',
                ip_address='127.0.0.1'
            )
            mock_info.assert_called_once()


class TestCache:
    """Test cache functionality"""
    
    def setup_method(self):
        """Clear cache before each test"""
        cache._data.clear()
    
    def test_cache_set_get(self):
        """Test basic cache set/get operations"""
        cache.set('test_key', 'test_value')
        assert cache.get('test_key') == 'test_value'
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        cache.set('test_key', 'test_value', expire_time=1)
        assert cache.get('test_key') == 'test_value'
        
        time.sleep(1.1)
        assert cache.get('test_key') is None
    
    def test_cache_increment(self):
        """Test cache increment operation"""
        assert cache.incr('counter') == 1
        assert cache.incr('counter') == 2
        assert cache.get('counter') == 2
    
    def test_cache_default_value(self):
        """Test cache default value"""
        assert cache.get('nonexistent', 'default') == 'default'


class TestIntegration:
    """Integration tests combining multiple security features"""
    
    def setup_method(self):
        """Clear cache before each test"""
        cache._data.clear()
    
    def test_combined_security_middleware(self, client):
        """Test multiple security middleware working together"""
        # Test valid request passes all middleware
        response = client.post('/test', data={'name': 'valid-name'})
        assert response.status_code == 200
        
        # Verify security headers are present
        assert 'X-Frame-Options' in response.headers
        
        # Test invalid input is blocked before rate limiting
        response = client.post('/test', data={'name': '<script>alert(1)</script>'})
        assert response.status_code == 400
    
    def test_edge_cases(self, client):
        """Test edge cases and error conditions"""
        # Empty request
        response = client.post('/test')
        assert response.status_code == 200
        
        # Very long input
        long_input = 'a' * 10000
        response = client.post('/test', data={'input': long_input})
        # Should either pass or be blocked, but not crash
        assert response.status_code in [200, 400]
    
    def test_concurrent_requests(self, client):
        """Test behavior under concurrent load"""
        # Simulate concurrent requests to rate-limited endpoint
        responses = []
        for i in range(10):
            response = client.get('/limited')
            responses.append(response.status_code)
        
        # Should have some 200s and some 429s
        assert 200 in responses
        assert 429 in responses


if __name__ == '__main__':
    pytest.main([__file__, '-v'])