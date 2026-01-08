FROM taigaio/taiga-back:latest

# Add OIDC authentication plugin for Taiga (Taiga 6)
# The contrib plugin is not published to PyPI; install from Git.
RUN apt-get update \
	&& apt-get install -y --no-install-recommends git ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir mozilla-django-oidc \
	&& pip install --no-cache-dir "git+https://github.com/taigaio/taiga-contrib-oidc-auth.git#subdirectory=back"

# Override settings to enable OIDC and mount urls under /api/oidc/
COPY settings/local.py /taiga-back/settings/local.py
COPY settings/urls.py /taiga-back/settings/urls.py
