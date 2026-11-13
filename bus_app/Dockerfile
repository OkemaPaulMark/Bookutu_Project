# ---- build the Flutter web app ----
FROM ghcr.io/cirruslabs/flutter:3.32.0 AS build
WORKDIR /src
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get
COPY . .
RUN flutter build web --release --base-href /

# ---- serve it; proxy API + media to the backend service ----
FROM caddy:2.8-alpine
COPY deploy/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /src/build/web /srv
