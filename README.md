# Tika parser for Paperless

The Paperless Project:

- [Original work](https://github.com/the-paperless-project/paperless/)
- [NG fork](https://github.com/jonaswinkler/paperless-ng/)

This parser adds support for many Office-type documents. Eg.: `.doc`, `.docx`, `.odt`, etc.

Those documents will be:

- parsed for their content, to enable search (using Tika)
- converted to PDF to enable web view (using Gotenberg)
- first page of PDF will be used for thumbnail (using the `paperless_tesseract` parser and ImageMagick)

The document will be downloadable in either original form, or the generated PDF.

## Usage

Add this parser in the `src/` directory of your Paperless installation.
If you are using Docker, you may mount it as a volume: `-v ./:/usr/src/paperless/src/paperless_tika/:ro`

You also need to add the plugin to the `INSTALLED_APPS` list in `paperless/settings.py`.

```python
INSTALLED_APPS = [
  ...
  "paperless_mail.apps.PaperlessMailConfig",
  "paperless_tika.apps.PaperlessTikaConfig", # Add this line
  ...
]
```

The plugin needs a Python module calles `tika`; I didn't find a nice way to install it in the upstream Docker image, so I built a new image:


```Dockerfile
FROM jonaswinkler/paperless-ng:0.9.9
RUN pip install tika
```

Then build it:

```bash
$ docker build -t paperless .
```

Finally, you need to have a Tika and Gotenberg server running.

When using Docker Compose, you can add the following to your YAML file:

```yaml
services:
  webserver:
    image: paperless # Our own image
    ...
    environment:
      PAPERLESS_APPS: paperless_tika.apps.PaperlessTikaConfig
      PAPERLESS_GOTENBERG: http://gotenberg:3000
      TIKA_SERVER_ENDPOINT: http://tika:9998

  gotenberg:
    image: thecodingmachine/gotenberg
    restart: unless-stopped
    environment:
      DISABLE_GOOGLE_CHROME: 1

  tika:
    image: apache/tika
    restart: unless-stopped
```
