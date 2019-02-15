alert_django
-------------

This package currently includes two containers based on the docker mysql and the scipy jupyter notebook images (see respective Dockerfiles for more details).

To use:
1. Create the network by running `./scripts/create_network.sh` in a terminal.
2. Build the mysql image with `./scripts/compose_mysql_build.sh`
3. Build the jupyter image with `./scripts/compose_jupyter_build.sh`
4. Start the mysql image with `./scripts/compose_mysql_up.sh`
5. Start the jupyter image with `./scripts/compose_jupyter_up.sh`

Note: the mysql image should preferably be up before starting the jupyter image.

To stop the images, run `./scripts/compose_***_stop.sh`
To destroy the content of the database, run `./scripts/compose_mysql_down.sh`

MySQL
------
Once the image running, MySQL is reachable at `0.0.0.0:40001` from outside of docker (e.g. local MySQL workbench), and at `alert_database_mysql:3306` from within docker (any container connecting to the *alert_bridge* network).

Default User settings:
- user: `root`
- pasword: `example`

Note that this simple setting should be changed for real life usage. 

Jupyter Notebook
----------------
Once the image running, Jupyter reachable from a browser at `0.0.0.0:8888`. To log into the notebook server, use the key `b2cd90e9a0dd` (also to be changed in a real life setting).
