FROM node:20-bookworm AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

FROM node:20-bookworm-slim AS runtime
ENV NODE_ENV=production
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip python3-venv curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system shadowwaves \
    && useradd --system --gid shadowwaves --create-home shadowwaves

COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY --from=build /app/dist ./dist
COPY python_src ./python_src

USER shadowwaves
EXPOSE 3100

CMD ["node", "dist/index.cjs"]
