FROM node:18-alpine

WORKDIR /app

# Copy package files first (better caching)
COPY package.json .

# Install dependencies
RUN npm install

# Copy the rest of the code
COPY . .

# Expose the Vite port
EXPOSE 5173

# Run the dev server exposed to the network
CMD ["npm", "run", "dev", "--", "--host"]