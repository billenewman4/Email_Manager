# Use the official Node.js image.
FROM node:18

# Create and change to the app directory.
WORKDIR /usr/src/app

# Copy application dependency manifests to the container image.
COPY package*.json ./

# Install production dependencies.
RUN npm install --only=production

# Copy local code to the container image.
COPY . .

# Set environment variables
ENV GCP_PROJECT_ID=primeval-truth-431023-f9
ENV NODE_ENV=production

# Run the web service on container startup.
CMD [ "node", "main.js" ]