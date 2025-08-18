import { trace, context } from '@opentelemetry/api';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

export class Tracer {
  private tracer: trace.Tracer;

  constructor() {
    const resource = Resource.default().merge(
      new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: 'lyra-api',
        [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
      })
    );

    this.tracer = trace.getTracer('lyra-api', '1.0.0');
  }

  async traceRequest(name: string, fn: () => Promise<any>): Promise<any> {
    const span = this.tracer.startSpan(name);
    
    try {
      const result = await context.with(
        trace.setSpan(context.active(), span),
        fn
      );
      span.setStatus({ code: trace.SpanStatusCode.OK });
      span.end();
      return result;
    } catch (error) {
      span.recordException(error as Error);
      span.setStatus({ 
        code: trace.SpanStatusCode.ERROR, 
        message: error instanceof Error ? error.message : 'Unknown error' 
      });
      span.end();
      throw error;
    }
  }

  createSpan(name: string, attributes?: Record<string, string | number | boolean>): trace.Span {
    const span = this.tracer.startSpan(name);
    if (attributes) {
      span.setAttributes(attributes);
    }
    return span;
  }

  async traceMiddleware(req: any, res: any, next: any): Promise<void> {
    const span = this.tracer.startSpan(`${req.method} ${req.path}`);
    
    span.setAttributes({
      'http.method': req.method,
      'http.url': req.url,
      'http.route': req.path,
      'user_agent.original': req.get('User-Agent') || '',
    });

    // Store span in request for use in other middleware
    req.span = span;

    res.on('finish', () => {
      span.setAttributes({
        'http.status_code': res.statusCode,
      });
      
      if (res.statusCode >= 400) {
        span.setStatus({ 
          code: trace.SpanStatusCode.ERROR,
          message: `HTTP ${res.statusCode}`
        });
      } else {
        span.setStatus({ code: trace.SpanStatusCode.OK });
      }
      
      span.end();
    });

    next();
  }
}