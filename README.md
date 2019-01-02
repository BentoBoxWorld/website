# Webtool
Webtool for BentoBox that allows users to create a ready to use .zip file with all desired addons in it.

[http://bentobox-tool.herokuapp.com]

### Deployment
1. Install Flask
2. pip install requirements.txt
3. export FLASK_APP = app.py
4. export FLASK_DEBUG = true (for debug)
5. flask run

However for production, I highly recommend using gunicorn or just running it on heroku.
