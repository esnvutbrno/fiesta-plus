# Buena Fiesta

_Buena means spanish great, so Fiesta is dead, long live Buena Fiesta!_

New generation of social network for helping international students - used by sections of Erasmus Student Network. 💜
By volunteers, for volunteers.

## Authors

Created with love and patiently maintained by [@esnvutbrno](https://github.com/esnvutbrno) members.

## Usage

Buena Fiesta is based on Docker containers orchestrized by Docker Compose.

### Requirements

For running the project, you need `docker-compose` with running Docker daemon.

### Development

`Makefile` in root of project provides following targets, which are pretty self-explaining. If you just want to run
project, hit the `up` target: `make up`.

```
check                Runs all included lints/checks/reformats
migrate              Runs manage.py migrate for all apps
makemigrations       Runs manage.py makemigrations for all apps
up                   Runs all needed docker containers in non-deamon mode
da                   Invokes django-admin command stored in CMD
build                Builds docker images.
help                 Shows help
```

### Production

_TBD_

## License

Distributed under the GNU GPLv3 License. See `LICENSE.txt` for more information.
