# Use Node.js 18 Alpine image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies first for better caching
COPY package*.json ./

# Clear npm cache and install dependencies
RUN npm cache clean --force && \
    npm install

# Copy all source files
COPY . .

# Build the React application
RUN npm run build

# Install serve globally to serve the built app
RUN npm install -g serve

# Expose port 3000
EXPOSE 3000

# Start the application using serve
CMD ["serve", "-s", "build", "-l", "3000"]