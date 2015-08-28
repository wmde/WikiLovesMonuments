# Wiki Loves Monuments

This repo is a collection of code enabling easier image uploads on the German Wikipedia for Wiki Loves Monuments competition.

The code consists of two parts:
1. Bots that analyze the monument pages and insert images from Commons in the monument lists. See the [bots README](update-bot/README.md) for detailed documentation on the bots.
2. A PHP script that forwards from Wikipedia links to the Commons Uploader, adding URL parameters. See the [forward script README](forward_script/README.md) for detailed documentation on the forward script.

## Deployment on Tool Labs
The tool name is `wlm-de-utils`. All following commands must be carried out with the tool account, *not* your personal Tool Labs account. To switch to the tool account, run the following command after logging in with your personal Tool Labs account:

    become wlm-de-utils

Generally, the [`WikiLovesMonuments`][wlmrepo] repository is checked out in the tool home directory.
Whenever you want to deploy a new version, just do a `git pull` in the repository directory. However, there are some things that must be done afterwards:

1. Update the `wlmbots` module:

 ```bash
 cd WikiLovesMonuments/update-bot
 pip install --update -e .
 ```

   If the installer displays a message that the module doesn't need to be updated, make sure that there were no changes in the Python code. If there were changes, change the version in `update-bot/setup.py`, commit, pull and install again.
2. Restart the commons bot:

 ```bash
 cd WikiLovesMonuments/update-bot
 jstop commons_bot
 jstart -l release=trusty -N commons_bot -cwd python -m wlmbots.commons_bot
 ```

 3. Update PHP libraries/autoloader

 ```bash
 cd WikiLovesMonuments/forward_script
 php ~/bin/composer.phar install --no-dev -o
 ```

### First-time initialization
The following steps have been taken manually on the Tool Labs server and *only* need to be done again if the account was somehow deleted/destroyed.

The relevant configuration files are in the directory [wlm-de-utils](wlm-de-utils/). All the files there must be placed in the home directory of the `wlm-de-utils` tool account.

#### Create a Python virtual environment
The command

    virtualenv ~/env

creates a [Python virtual environment][virtualenv] where modules can be installed without root permissions and without affecting the rest of the system. Copy the files [`.bashrc`](wlm-de-utils/.bashrc) and [`.bash_profile`](wlm-de-utils/.bash_profile) to the tool home directory to ensure that the virtual environment is activated whenever the tool account is used.

To manually activate the environment without logging out, use the command

```bash
source $HOME/env/bin/activate
```

#### Set up the bot environment
Follow the install instructions in the [README file for the bot](update-bot/README.md).

Create a password file named `WikiLovesMonuments/update-bot/secretsfile`. The contents of the file should look like this:

    ("WLMUploadVorlageBot", "password-of-the-bot")

Replace the password and set the file access to only the user (chmod 600).

Add the following line to the user-config.py:

    password_file = "secretsfile"

#### Set up the web server
1. Set up composer like described at https://getcomposer.org/ and do a `composer install` in the `forward_script` directory.
2. Create a symbolic link:

    ```bash
    rm -r public_html
    ln -s WikiLovesMonuments/forward_script/web public_html
    ```

3. Copy the file [`.lighttpd.conf`](wlm-de-utils/.lighttpd.conf) to the home directory.
4. Start the web server with the command

    ```bash
    webservice start
    ```

5. Copy the file `WikiLovesMonuments/forward_script/app_settings.local.php.dist` to `WikiLovesMonuments/forward_script/app_settings.local.php` and edit the file to accommodate for the local environment. In case of Tool Labs, this means uncommenting the line for the pageinfo script.


[wlmrepo]: https://github.com/wmde/WikiLovesMonuments/
[virtualenv]: https://virtualenv.pypa.io/en/latest/
[tools_grid]: https://wikitech.wikimedia.org/wiki/Help:Tool_Labs/Grid
