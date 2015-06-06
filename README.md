#iBlock - the tool for blocking Apple IDs
If you use Linux, then you'll get translations!

##Requirements
* Python >=3.2

##Usage
`./iblock.py [opts]`

##Options
###--help, -h            
Show help message and exit.
###--version, -v         
Show program's version number and exit.
###--login, -l        
Get access to VK.com

For getting token we're using `vk_api_auth` lib. You can find it's sources in one's directory.
###--update, -u
Check for updates.
###--interval {...}, -i {...}
Set scanning interval (in minutes).

**Type:** number

**Default:** 3.0
###--posts {...}, -p {...}
Set posts limit for scanning

**Type:** integer number

**Default:** 50
###--groups {...}, -g {...}
Specify groups where the program will look for Apple IDs *(separated by comma)*.

For example: `... -g https://vk.com/myoastore,irocketapps`
###--ids {...}, -I {...}
Specify groups where the program will look for Apple IDs *(separated by comma)*.

For example: `... -I example@mail.com,cock@icloud.com`

##Configuration file
*See* `iBlock_README.ini` *for commentaries to configuration.*

##Used libraries
* [xmltodict](https://github.com/martinblech/xmltodict)
* [vk_api_auth](https://github.com/dzhioev/vk_api_auth)
* [timeout-decorator](https://github.com/pnpnpn/timeout-decorator)