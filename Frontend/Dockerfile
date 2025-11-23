# Stage 1: Build the static assets
FROM node:20 as builder

# Set working directory
WORKDIR /app

# Install dependencies
COPY package.json .
COPY package-lock.json .
RUN npm install

# Build the application
COPY . .
RUN npm run build 

# Stage 2: Build the nginx image to serve the static assets build in builder stage
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80
