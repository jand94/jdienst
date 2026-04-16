FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json /app/
RUN npm ci --no-audit --no-fund

COPY . /app

EXPOSE 3000

CMD ["sh", "-c", "npm run dev -- --hostname ${HOSTNAME:-0.0.0.0} --port ${PORT:-3000}"]
