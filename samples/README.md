### Starting the Flask server
```bash
FLASK_APP=app.py flask run
```

### Example curls for hitting sample app endpoints
```bash
curl -XGET 'http://127.0.0.1:5000/executePageload?tntId=12345'
curl -XGET 'http://127.0.0.1:5000/executeMbox?mbox=navbar&tntId=12345'
curl -XGET 'http://127.0.0.1:5000/prefetchMbox?prefetch=cart&mbox=navbar&tntId=12345'
curl -XGET 'http://127.0.0.1:5000/prefetchView?view=home,cart&tntId=12345'
curl -XGET 'http://127.0.0.1:5000/prefetchView?view=home&tntId=12345&async=true'
curl -XGET 'http://127.0.0.1:5000/prefetchViewAsyncio?view=home,cart&tntId=12345&async=true'
curl -XPOST 'http://127.0.0.1:5000/sendNotifications?tntId=12345' -d '{"mboxes":[{"name":"cart","event_tokens":["rI03nB2aB/8ANKbtolR1i2qipfsIHvVzTQxHolz2IpSCnQ9Y9OaLL2gsdrWQTvE54PwSz67rmXWmSnkXpSSS2Q=="]}]}'
```