FROM node:20-alpine AS plugin_build

RUN apk add --no-cache curl unzip python3 make g++
WORKDIR /src

# Build the Taiga OIDC frontend plugin (use codeload to avoid git clone restrictions)
RUN mkdir -p /tmp/oidc \
	&& curl -fsSL -o /tmp/oidc/oidc.zip https://codeload.github.com/taigaio/taiga-contrib-oidc-auth/zip/refs/heads/master \
	&& unzip -q /tmp/oidc/oidc.zip -d /tmp/oidc \
	&& mv /tmp/oidc/taiga-contrib-oidc-auth-* /src/taiga-contrib-oidc-auth

WORKDIR /src/taiga-contrib-oidc-auth/front

RUN npm install
RUN npm install gulp
RUN npx gulp build

FROM taigaio/taiga-front:latest

# Copy compiled plugin assets
RUN mkdir -p /usr/share/nginx/html/plugins/oidc-auth/
COPY --from=plugin_build /src/taiga-contrib-oidc-auth/front/dist/ /usr/share/nginx/html/plugins/oidc-auth/

# The upstream plugin repository ships the template as a .jade partial; the published dist
# doesn't include the compiled HTML. Taiga expects this file at runtime.
RUN cat > /usr/share/nginx/html/plugins/oidc-auth/oidc_auth.html <<'EOF'
<div tg-oidc-login-button>
	<a class="button button-auth" href="" title="Enter with your {{ buttonText }} account">
		<img src="plugins/oidc-auth/images/contrib/{{ buttonImage }}" alt="" style="vertical-align:middle" />
		<span>{{ buttonText }}</span>
	</a>
</div>
EOF

# Make plugin asset URLs subpath-safe by using relative paths.
RUN sed -i \
		-e 's#"template": "/plugins/oidc-auth/oidc_auth.html"#"template": "plugins/oidc-auth/oidc_auth.html"#' \
		-e 's#"js": "/plugins/oidc-auth/oidc_auth.js"#"js": "plugins/oidc-auth/oidc_auth.js"#' \
		/usr/share/nginx/html/plugins/oidc-auth/oidc-auth.json

# The compiled JS embeds a template and image URLs rooted at /plugins/...; make them relative so
# they resolve under TAIGA_SUBPATH (e.g. /kanban/plugins/...).
RUN sed -i 's#/plugins/oidc-auth/#plugins/oidc-auth/#g' /usr/share/nginx/html/plugins/oidc-auth/oidc_auth.js
