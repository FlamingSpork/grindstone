## moving-image sampler

usage:

```
uv venv

time uv run main.py render -d Z ../data/12-14_15-11
```

if you're dockerizing:
but I wouldn't recommend dockerizing.
```
docker run -it -v /home/philo/Programming/linecam:/linecam -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY -h $HOSTNAME -v $HOME/.Xauthority:/home/philo/.Xauthority grindstone
```

```bash
ls -d /tmp/02-03_10-55/* | sort | ./infinite-image-scroller.py -f - -dr -s0

convert +append /tmp/02-03_10-55/out-00{04..10}.jpeg a.tif
```
