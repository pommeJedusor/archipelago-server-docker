## purpose of the repository

the purpose of this repository is to make it easier to deploy an archipelago room using docker

when the docker container starts, it looks if the game has already been generated, if not it generates it, then in both cases it starts hosting the room

## how to use

to run either use docker-compose and modify the docker-compose.yaml how you want or use the following command and modify it how you want:
```bash
docker run -v ./host.yaml:/archipelago/Archipelago/host.yaml -v ./Players/:/archipelago/Archipelago/Players/ -v ./custom_worlds:/archipelago/Archipelago/custom_worlds/ -v ./output:/archipelago/Archipelago/output/ -p 38281:38281 pommejedusor/archipelago_server:latest
```


volumes:
- `custom_wordls` should store the apworld of the custom games you want to support and that aren't already supported
- `Players` should hold the yaml files for each player
- `host.yaml` is simply the host.yaml file and should hold the desired settings
- `output` shouldn't have anything in it before running the container it will once ran hold the AP_\*.zip file and the AP_\*.apsave
