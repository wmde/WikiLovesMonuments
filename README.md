# Wiki Loves Monuments

This repo is a collection of code enabling easier image uploads on the German Wikipedia for Wiki Loves Monuments competition.

The code consists of two parts:

1. Bots that analyze the monument pages and insert images from Commons in the monument lists. See the [bots README](update-bot/README.md) for detailed documentation on the bots.
2. A Python script that forwards from Wikipedia links to the Commons Uploader, adding URL parameters. See the [forward script README](forward_script_python/README.md) for detailed documentation on the forward script.

## Deployment on Tool Labs
The tool name is `wlm-de-utils`. All following commands must be carried out with the tool account, *not* your personal Tool Labs account. To switch to the tool account, run the following command after logging in with your personal Tool Labs account:

    become wlm-de-utils

Generally, the [`WikiLovesMonuments`][wlmrepo] repository is checked out in the tool home directory.
Whenever you want to deploy a new version, just do a `git pull` in the repository directory. However, there are some things that must be done afterwards:

1. Restart the web service:

 ```bash
 webservice stop
 webservice --release trusty uwsgi-plain start
 ```

2. Restart the commons bot:

 ```bash
 cd WikiLovesMonuments/update-bot
 jstop commonsbot
 jstart -N commonsbot -l release=trusty -wd /data/project/wlm-de-utils/WikiLovesMonuments/update-bot/ /data/project/wlm-de-utils/WikiLovesMonuments/update-bot/run_commonsbot.sh
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

#### Install the python modules
Make sure that the Python virtual environment (see above) is activated. Then follow the install instructions from [README file for the forward script](forward_script_python/README.md).

#### Set up the forward script
1. Copy the configuration file [uwsgi.ini](wlm-de-utils/uwsgi.ini) to the home directory.

2. Create the file `settings.py` in the home directory. You can use the [template](wlm-de-utils/settings.py.dist) from the `wlm-de-utils directory. You must fill the variable `REDIS_CACHE_PREFIX` with a random string, for example one generated with the command

 ```bash
 openssl rand -base64 32
 ```

3. Start the web service with the command

 ```bash
 webservice --release trusty uwsgi-plain start
 ```

You can monitor the file `uwsgi.log` in the home directory to check if the web server is running. When a line containing `spawned uWSGI worker` shows up, the script is ready. Test with the link
`https://tools.wmflabs.org/wlm-de-utils/redirect/Liste_der_Baudenkmäler_in_Abtswind/wlm-de-by?id=D-6-75-111-5&lat=49.77168&lon=10.37051` to check if the redirect works.

[wlmrepo]: https://github.com/wmde/WikiLovesMonuments/
[virtualenv]: https://virtualenv.pypa.io/en/latest/
[tools_grid]: https://wikitech.wikimedia.org/wiki/Help:Tool_Labs/Grid
