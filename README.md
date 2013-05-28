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

    $ storm add [-h]  [--id_file ID_FILE] name connection_uri

Where `-h`, `id_file` are optional arguments.

example:

    $ storm add my_vps root@emreyilmaz.me:22
    my_vps added to your ssh config. you can connect it by typing "ssh my_vps".

### modifying hosts

    storm edit [-h] [--id_file ID_FILE] name connection_uri

Where `-h`, `id_file` are optional arguments.

example:

    $ storm edit my_vps emre@emreyilmaz.me:2400
    "my_vps" updated successfully.

### deleting a single host

    $ storm delete name

example:

    $ storm delete my_vps
    success hostname "my_vps" deleted successfully.
    
### searching hosts
    $ storm search git
    Listing results for git:
      github -> emre@github.com:22


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
    
## connection_uri format

    - user@server:port
    - server:port
    - server
        
defaults for user -> $USER, port -> 22

/see <a href="https://github.com/emre/storm/blob/master/storm/ssh_uri_parser.py">ssh_uri_parser</a> for further look.

## contributors

-   <a href="http://github.com/ras0ir">@ras0ir</a> - PKGBUILD for Archlinux and testing excessive ssh configs.</a>
-   <a href="http://github.com/benvand">@benvand</a>
-   <a href="http://github.com/Bengt">@Bengt</a>
-   <a href="http://github.com/henrysher">@henrysher</a>
-   <a href="http://github.com/playpauseandstop">@playpauseandstop</a>
