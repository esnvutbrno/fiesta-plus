# Buena Fiesta

_Buena means spanish great, so Fiesta is dead, long live Buena Fiesta!_

New generation of social network for helping international students - used by sections of Erasmus Student Network. 💜
By volunteers, for volunteers.

## Authors

Created with love and patiently maintained by [@esnvutbrno](https://github.com/esnvutbrno) members.

## Usage

Buena Fiesta is based on Docker containers orchestrized by Docker Compose.

### Requirements

For running the project, you need `docker compose` plugin with running Docker daemon.

### Development

`Makefile` in root of project provides following targets, which are pretty self-explaining. If you just want to run
project, hit the `up` target: `make up`.

```
pre-commit                       Runs all included lints/checks/reformats
seed                             Seed database with fake data.
startplugin                      Create plugin in project with name=
shell_plus                       Starts django shell_plus
migrate                          Runs manage.py migrate for all apps
check                            Runs all Django checks.
makemigrations                   Runs manage.py makemigrations for all apps
loadlegacydata                   Loads all data from legacydb run from ./legacy.sql.
test                             Runs django test cases.
graph_models                     Plot all Django models into models.png
da                               Invokes django-admin command stored in cmd=
build                            Builds docker images.
upb                              Build and runs all needed docker containers in non-deamon mode
upbd                             Build and runs all needed docker containers in detached mode
upd                              Runs all needed docker containers in detached mode
up                               Runs all needed docker containers
produp                           Runs fiesta in production mode.
help                             Shows help
generate-localhost-certs         Generates self-signed localhost certs for working HTTPS.
setup-elastic                    Starts elasticsearch standalone an generates keystore and passwords for all users.
trust-localhost-ca               Copies generted CA cert to trusted CA certs and updates database -- requires sudo.
```

### Production

_TBD_

## License

Distributed under the GNU GPLv3 License. See `LICENSE.txt` for more information.
