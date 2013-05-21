storm
=====

storm is a command line tool to manage your hosts at sshconfig.

<img src="https://raw.github.com/emre/storm/master/ss.png">

### installation ###

```
pip install stormssh
```
or if you like 90s:

```
easy_install stormssh
```

or add storm directory to the your path.

### getting started ###

**adding hosts**
 ```
 storm add [-h] [--port PORT] [--id_file ID_FILE] name host user
 ```
 
 id_file and port are optional arguments.
 
example:
```
$ storm  add my_vps emreyilmaz.me root
my_vps added to your ssh config. you can connect it by typing "ssh my_vps".
```

**modifying hosts**
```
storm edit [-h] [--port PORT] [--id_file ID_FILE] name host user
```
 
 id_file and port are optional arguments.
 
example:
```
$ storm  edit my_vps emreyilmaz.me emre --port=88
"my_vps" updated successfully.
```

**deleting a single host**
```
storm delete  name
```
  
example:
```
$ storm delete my_vps
success  hostname "my_vps" deleted successfully.
```

**listing hosts**
```
$ storm list
Listing hosts:
  vps -> 22@emreyilmaz.me:22
  netscaler -> root@127.0.0.1:8081
```

**deleting all hosts**
```
$ storm delete_all
all entries deleted.
```
