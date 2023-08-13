
# Buena Fiesta

![python](https://img.shields.io/badge/python-3.11-ffd343?style=flat)
![django](https://img.shields.io/badge/Django-4.2-0C4B33?style=flat)
![kubernetes](https://img.shields.io/badge/Kubernetes-1.26-316ce6?style=flat)
![tailwind css](https://img.shields.io/badge/Tailwind_CSS-3.3-38BDF8?style=flat)
![nginx](https://img.shields.io/badge/Nginx-1.25-009639?style=flat)

![last commit](https://img.shields.io/github/last-commit/esnvutbrno/buena-fiesta)
![cluster deploy](https://github.com/esnvutbrno/buena-fiesta/actions/workflows/deploy.yml/badge.svg)
![licence](https://img.shields.io/github/license/esnvutbrno/buena-fiesta)

_Buena means spanish great, so Fiesta is dead, long live Buena Fiesta!_

New generation of social network for helping international students - used by sections of Erasmus Student Network. 💜
By volunteers, for volunteers.

## Development

0. for local development is `docker`, `docker compose`, `make` needed

1. After cloning, prepare local `.env` file:
```shell
cp .env.template .env
```

2. Generate secret key for Django:
```shell
sed -ie "s/DJANGO_SECRET_KEY=$/DJANGO_SECRET_KEY=$(echo $RANDOM | md5sum | head -c 20)/" .env
```

If you want to run fiesta on other domain than `fiesta.test`, adjust the `ROOT_DOMAIN` variable.

3. Prepare Webpack dependencies:
```shell
make dc cmd="run webpack yarn"
```

4. Run database migrations:
```shell
make migrate
```

5. Prepare admin account
```shell
make da cmd=createsuperuser
```

6. Start the docker compose:
```shell
make up
```

You should see running Django:

```
buena-fiesta-web-1          | Django version 4.2.1, using settings 'fiesta.settings'
buena-fiesta-web-1          | Starting development server at http://0.0.0.0:8000/
```

And webpack compiling the assets:

```
buena-fiesta-webpack-1      | asset main.22bd896b.js 1.37 MiB [emitted] [immutable] (name: main)
buena-fiesta-webpack-1      | asset main.22bd896b.css 316 KiB [emitted] [immutable] (name: main)
buena-fiesta-webpack-1      | Entrypoint main 1.68 MiB = main.22bd896b.css 316 KiB main.22bd896b.js 1.37 MiB¨
...
buena-fiesta-webpack-1      | webpack 5.78.0 compiled successfully in 5852 ms
```

7. Make sure domain `fiesta.test` (or your preferred domain from step 2) is pointing to localhost or device IP (use `/etc/hosts`) and `webpack.fiesta.test` to load the project styles.
```
[local_host_ip] fiesta.test webpack.fiesta.test
```

8. Open `http://fiesta.test` and profit!

### Development tips:
* use `make generate-local-certs` if you want to HTTPS in local environment -- restart of containers is needed afterward
* Django and Webpack are watching the files via inotify, so no restart is needed after code changes
* if you accidentally kill some of the containers, you can resurrect them with `make upd` in another shell to have them up faster
* `make shell_plus` runs Django shell plus console, interactive tool with all Django models preloaded
* `make makemigrations` and `migrate` are you friends on your Django journey
* see [Demo Data Fixtures](#demo-data-fixtures) for some demo data to play with, or use `make seed` to generate some fake data (check the [seed command](./fiesta/apps/utils/management/commands/seed.py) for more info)
* `Makefile` included in project provides a few self-explanatory useful targets:

```
pre-commit                       Runs all included lints/checks/reformats
seed                             Seed database with fake data.
clean_unlinked                   Cleans all unlinked data from database.
startplugin                      Create plugin in project with name=
shell_plus                       Starts django shell_plus
migrate                          Runs manage.py migrate for all apps
optimizemigration                Optimize last migration by optimizemigration: app= migration=
check                            Runs all Django checks.
makemigrations                   Runs manage.py makemigrations for all apps
loadlegacydata                   Loads all data from legacydb run from ./legacy.sql.
test                             Runs django test cases.
graph_models                     Plot all Django models into models.png
da                               Invokes django-admin command stored in cmd=
dc                               Invokes docker compose command stored in cmd=
build                            Builds docker images for development.
upb                              Build and runs all needed docker containers in non-deamon mode
upbd                             Build and runs all needed docker containers in detached mode
upd                              Runs all needed docker containers in detached mode
up                               Runs all needed docker containers
produp                           Runs fiesta in (local)production mode.
psql                             Runs psql shell in database
dumpdb                           Dumps database to .sql
loaddb                           Loads database from dump=
help                             Shows help
generate-local-certs             Generates self-signed *.${ROOT_DOMAIN} certs for working HTTPS.
setup-elastic                    Starts elasticsearch standalone an generates keystore and passwords for all users.
trust-localhost-ca               Copies generted CA cert to trusted CA certs and updates database -- requires sudo.
```


### Demo Data

For demo your can use included fixtures with the ESN Hawaii and some users to test it out. To load them run:

```shell
make loaddata fixture=fiesta/fiesta/fixtures/01_demo_admin.json
make loaddata fixture=fiesta/fiesta/fixtures/02_demo_section-universities.json
make loaddata fixture=fiesta/fiesta/fixtures/03_demo_users.json
make loaddata fixture=fiesta/fiesta/fixtures/04_demo_base-plugins.json
```

The single included section is `ESN Hawaii` with enabled two crucial plugins: Dashboard and ESN section plugin -- usually it runs ons `esnhawaii.fiesta.test`, so don't forget to add it to your `/etc/hosts` file.
It has the following users:

| username/password  | role                  |
|--------------------|-----------------------|
| `admin`            | Django superuser      |
| `walter.white`     | section admin         |
| `anna.gunn`        | section editor        |
| `jesse.pinkman`    | section member        |
| `aaron.paul`       | section member        |
| `gus.fring`        | section international |
| `hector.salamanca` | section international |

## Contributing

Use Pull requests -- [how to prepare a great PR?](https://github.blog/2015-01-21-how-to-write-the-perfect-pull-request/)


## Authors

Created with love and maintained by [@esnvutbrno](https://github.com/esnvutbrno) members.

## License

Distributed under the GNU GPLv3 License. See `LICENSE.txt` for more information.
