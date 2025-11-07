# Optimized Nginx with custom configuration
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Copy static files
COPY --chown=nginx:nginx dist/ /usr/share/nginx/html/

# Add health check script
RUN echo '#!/bin/sh' > /health.sh && \
    echo 'curl -f http://localhost/health || exit 1' >> /health.sh && \
    chmod +x /health.sh

# Security: Run as non-root
RUN chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

USER nginx

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD /health.sh

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
