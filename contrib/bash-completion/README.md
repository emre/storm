# Bash Completion for StormSSH

Complete your SSH actions like a Boss!

## Installation

You can download bash script and add it to your environment. All you need
is to source it!

    cd /path/to/your/env/
    curl -O https://raw.githubusercontent.com/emre/storm/master/contrib/bash-completion/stormssh
    
    # add it to you .bashrc or so,
    source /path/to/your/env/storm

or, if you are an OSX user, you can download it from `brew`:

    brew install homebrew/completions/stormssh-completion

## Usage

Completes your **Host** names in required commands such as; `clone` `delete`
`edit` `move` `update`

    $ storm [TAB]
    add         clone       delete_all  list        search      version     
    backup      delete      edit        move        update      web
    
    # completes your Hosts :)
    $ storm clone [TAB]
    you_connection_name1    you_connection_name3  you_connection_name5      you_connection_name7
    you_connection_name2    you_connection_name4  you_connection_name6      you_connection_name8

