FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

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