# SHOTOKAN Web: one image with the built site, the API and the publish tool.
# build:  docker build -f docker/Dockerfile -t shotokan-web .

FROM node:22-alpine AS web
WORKDIR /src/web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
RUN npm run build

FROM python:3.12-slim
ARG VERSION=dev
LABEL org.opencontainers.image.title="SHOTOKAN Web" \
      org.opencontainers.image.source="https://github.com/shotokan-sf6/web" \
      org.opencontainers.image.version="${VERSION}" \
      dev.hogberg.shotokan.schema-major="1"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    SHOTOKAN_DB=/data/current.db SHOTOKAN_STATIC=/app/web SHOTOKAN_PORT=8080
WORKDIR /app
COPY api/requirements.txt api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt
COPY api/app api/app
COPY publish publish
COPY --from=web /src/web/build web
COPY docker/entrypoint.sh /usr/local/bin/shotokan
RUN chmod +x /usr/local/bin/shotokan && rm -rf publish/out \
 && useradd --system --uid 10001 --home /app shotokan && mkdir -p /data && chown shotokan /data /app/publish
USER shotokan
VOLUME /data
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request,os;urllib.request.urlopen('http://127.0.0.1:%s/healthz'%os.environ['SHOTOKAN_PORT'])" || exit 1
ENTRYPOINT ["shotokan"]
CMD ["serve"]
