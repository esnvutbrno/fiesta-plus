#!/bin/bash

chown 1000:1000 -R /usr/src/ && chmod a+wx -R /usr/src/media && chmod a+wx -R /usr/src/static
exec su 1000 -c "$*"
