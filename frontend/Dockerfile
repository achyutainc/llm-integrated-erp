FROM node:20-slim

WORKDIR /app

# Copy package.json from the frontend directory (relative to build context root)
COPY frontend/package*.json ./
RUN npm install

# Copy the rest of the frontend code
COPY frontend/ .

CMD ["npm", "run", "dev", "--", "--host"]
