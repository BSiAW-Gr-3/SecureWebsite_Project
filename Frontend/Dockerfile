# Stage 1: Build the static assets
FROM node:20 as builder

WORKDIR /app

# Copy package files and install dependencies
COPY package.json .
COPY package-lock.json .
RUN npm install

# Copy source code and build
COPY . .
# THIS IS THE CRITICAL STEP: Build for production
RUN npm run build 

# Stage 2: Serve the static assets using a light web server (e.g., Nginx)
FROM nginx:alpine

# -----------------------------------------------------------------
# The default config is at /etc/nginx/conf.d/default.conf, 
# but copying over the full nginx.conf is simpler.
COPY nginx.conf /etc/nginx/conf.d/default.conf
# -----------------------------------------------------------------

# Copy the built files from the builder stage into the Nginx public directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 (standard Nginx port)
EXPOSE 80
