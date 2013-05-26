# storm

storm is a command line tool to manage your ssh connections.

<img src="https://raw.github.com/emre/storm/master/ss.png">

## installation

    $ [sudo] pip install stormssh

or if you like 90s:

    $ [sudo] easy_install stormssh

or download add storm directory to the your `$PATH`. E.g.

    $ git clone git://github.com/emre/storm.git
    $ export PATH=$PATH:`pwd`/storm/storm/bin/; storm

## getting started

### adding hosts

    $ storm add [-h] [--port PORT] [--id_file ID_FILE] name host user

Where `-h`, `id_file` and `port` are optional arguments.

example:

    $ storm add my_vps emreyilmaz.me root
    my_vps added to your ssh config. you can connect it by typing "ssh my_vps".

### modifying hosts

    storm edit [-h] [--port PORT] [--id_file ID_FILE] name host user

Where `-h`, `id_file` and `port` are optional arguments.

example:

    $ storm edit my_vps emreyilmaz.me emre --port=88
    "my_vps" updated successfully.

### deleting a single host

    $ storm delete name

example:

    $ storm delete my_vps
    success hostname "my_vps" deleted successfully.

### listing hosts

    $ storm list
    Listing hosts:
      vps -> 22@emreyilmaz.me:22
      netscaler -> root@127.0.0.1:8081

### deleting all hosts

    $ storm delete_all
    all entries deleted.

## known issues

If you use zsh on a mac and get "command not found: storm" for main storm script, make sure you have storm in your PATH.

example:

    $ export PATH=$PATH:/usr/local/share/python/; storm

## contributors

-   <a href="http://github.com/ras0ir">Samed Beyribey</a> - PKGBUILD for Archlinux and testing excessive ssh configs.</a>
-   <a href="http://github.com/benvand">@benvand</a>
