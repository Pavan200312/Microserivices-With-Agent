FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Build the app for production
RUN npm run build

# Install serve to run the production build
RUN npm install -g serve

EXPOSE 3000

# Serve the production build
CMD ["serve", "-s", "dist", "-l", "3000"]
