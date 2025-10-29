# Use node image for building React app
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Build the production bundle
RUN npm run build

# --- Production server stage ---
FROM node:20-alpine AS serve
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/build ./build

EXPOSE 3000
CMD ["serve", "-s", "build"]
