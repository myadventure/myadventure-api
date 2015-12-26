# myadventure-api

## Build Docker image
```
docker build -t="myadventure/myadventure-api" .
```

## Run Docker container
```
docker run -P -t -i -v $(CURDIR)/app:/opt/app myadventure/myadventure-api
```
