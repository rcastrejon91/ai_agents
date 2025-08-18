import logging
import json
from datetime import datetime
import traceback
from flask import request
import uuid

class CustomJSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'request_id': getattr(record, 'request_id', None)
        }

        if hasattr(record, 'request'):
            log_record.update({
                'method': record.request.method,
                'path': record.request.path,
                'ip': record.request.remote_addr
            })

        if record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

        return json.dumps(log_record)

def setup_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(CustomJSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def request_id_middleware():
    request.id = str(uuid.uuid4())