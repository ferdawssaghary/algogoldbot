FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (more tolerant than npm ci)
RUN npm config set legacy-peer-deps true \
    && npm install --no-audit --no-fund

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Expose port
EXPOSE 3000

# Install serve to serve static files
RUN npm install -g serve

# Start the application
CMD ["serve", "-s", "build", "-l", "3000"]