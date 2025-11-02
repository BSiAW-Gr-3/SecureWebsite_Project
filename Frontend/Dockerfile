# Stage 1: Build the static assets
FROM node:20 as builder

# Create a non-root user for build stage
RUN groupadd -g 1001 appgroup && \
    useradd -r -u 1001 -g appgroup appuser

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json .
COPY package-lock.json .

# Set build argument for API URL with default value
ARG VITE_API_URL=https://rybmw.space
ENV VITE_API_URL=$VITE_API_URL

# Install dependencies as root
RUN npm install

# Copy application files and change ownership
COPY --chown=appuser:appgroup . .

# Build the application
RUN npm run build 


# Stage 2: Build the nginx image to serve the static assets
FROM nginx:alpine

# Create a non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static assets from builder stage
COPY --from=builder --chown=appuser:appgroup /app/dist /usr/share/nginx/html

# Change nginx to run as non-root user
RUN touch /var/run/nginx.pid && \
    chown -R appuser:appgroup /var/cache/nginx /var/run/nginx.pid /etc/nginx/conf.d

# Switch to non-root user
USER appuser

# Expose port 80
EXPOSE 8080
