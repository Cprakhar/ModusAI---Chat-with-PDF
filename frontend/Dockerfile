# Frontend Dockerfile
FROM node:22-alpine

WORKDIR /app

COPY package.json ./
COPY pnpm-lock.yaml ./
COPY . ./

RUN npm install -g pnpm && pnpm install

# Build the Next.js app
RUN pnpm build

EXPOSE 3000

CMD ["pnpm", "start"]
