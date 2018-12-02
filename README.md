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
    postgres=# CREATE USER domain_blacklist WITH PASSWORD 'domain_blacklist';
    CREATE ROLE
    postgres=# CREATE DATABASE domain_blacklist;
    CREATE DATABASE
    postgres=# GRANT ALL PRIVILEGES ON DATABASE domain_blacklist TO domain_blacklist;
    GRANT
    ```
    Execute ddl script:
    ```
    $ psql -U domain_blacklist -h localhost
    Password for user domain_blacklist: 
    psql (9.5.14)
    SSL connection (protocol: TLSv1.2, cipher: ECDHE-RSA-AES256-GCM-SHA384, bits: 256, compression: off)
    Type "help" for help.

    domain_blacklist=> \i schema.ddl 
    CREATE TABLE
    CREATE TABLE
    ALTER TABLE
    domain_blacklist=> 
    ```

4. Run pox with extension:
    ```
    ./pox.py domain-blacklist log.level --DEBUG
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

