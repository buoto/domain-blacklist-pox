domain-blacklist-pox
=======

# Setup

1. Clone pox repo [github.com/noxrepo/pox](https://github.com/noxrepo/pox).

2. Move this repo ([domain-blacklist-pox](https://github.com/buoto/domain-blacklist-pox)) to `ext/` dir in pox repo.

3. Setup PostgreSQL database
    Create user and database:
    ```
    $ sudo su
    $ su - postgres
    $ psql
    postgres=# CREATE USER <shell username>;
    CREATE ROLE
    postgres=# CREATE DATABASE domain_blacklist;
    postgres=# \c domain_blacklist
    You are now connected to database "domain_blacklist" as user "postgres".
    postgres=# GRANT ALL PRIVILEGES on all tables in schema public to <shell username>;
    GRANT
    ```
    Initiate database:
    ```
    $ python init_db.py
    ```

4. Run pox with extension:
    ```
    $ make install
    $ make run
    ```
    In another terminal you can manage blacklisted domains:
    ```
    $ python cli.py list
    No blacklisted domains.
    ```

# Demo
Download mininet VirtualBox image from [github.com/mininet/mininet/wiki/Mininet-VM-Images](https://github.com/mininet/mininet/wiki/Mininet-VM-Images).

Import it in VirtualBox and then in settings change network adapter to "bridged adapter".
That will expose your host's network interface in VM, which will be usefull in further steps.

Now you can run mininet host in background with:
```
VBoxManage startvm Mininet-VM --type headless
```

On mininet host run (<host-ip> is your ):
```
sudo mn -x --topo single,1 --nat --controller remote,ip=<host-ip>
```

