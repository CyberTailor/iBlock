#!/bin/bash

# Use this tool to update translations

cd locale/ru/LC_MESSAGES
msgfmt iblock.po
mv messages.mo iblock.mo
cd ../../..
