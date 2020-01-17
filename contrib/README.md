# Contrib

This folder contains some contrib code

## Dockerfile

The Dockerfile allows to containerize the app.

The build can be done as:

```shell
docker build -t docker.io/myuser/xiaomi-ble-mqtt:latest -f contrib/Dockerfile .
```

Then, it can be executed as:

```shell
docker run --net=host --name="xiaomi-ble-mqtt" --rm -v /home/user/xiaomi-ble-mqtt/:/config docker.io/myuser/xiaomi-ble-mqtt:latest
```

Where `/home/user/xiaomi-ble-mqtt/` contains the configuration files (`mqtt.ini` and `devices.ini`)

## multi-arch-manifest.yaml

In order to have different container images for different architectures (amd64 and armv7 for instance) using the same tag (for instance `xiaomi-ble-mqtt:latest`) in Dockerhub, it is required to craft a special manifest. This can be done with `docker manifest` or using [`manifest-tool`](https://github.com/estesp/manifest-tool).

The process is as follows:

* Create a container image for every architecture:

```shell
# In a x86_64 linux host:
docker build -t docker.io/myuser/xiaomi-ble-mqtt:amd64 -f contrib/Dockerfile .

# In a armv7 linux host (raspberry pi):
docker build -t docker.io/myuser/xiaomi-ble-mqtt:armv7 -f contrib/Dockerfile .

# In a arm64 linux host (pine64):
docker build -t docker.io/myuser/xiaomi-ble-mqtt:arm64 -f contrib/Dockerfile .
```

* Create an account in dockerhub and login:

```shell
docker login
```

* Push it to dockerhub:

```shell
# In the x86_64 linux host:
docker push docker.io/myuser/xiaomi-ble-mqtt:amd64

# In the armv7 linux host (raspberry pi):
docker push docker.io/myuser/xiaomi-ble-mqtt:armv7

# In the arm64 linux host (pine64):
docker push docker.io/myuser/xiaomi-ble-mqtt:arm64
```

* Upload the multiarch manifest (modify it to use your user first):

```shell
manifest-tool --username youruser --password yourpassword push from-spec contrib/multi-arch-manifest.yaml
```

Then, from an amd64/armv7/arm64 host:

```shell
docker pull docker.io/myuser/xiaomi-ble-mqtt:latest
```
