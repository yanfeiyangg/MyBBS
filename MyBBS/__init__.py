# 这是为了确保在django启动时启动 celery
from __future__ import absolute_import
from .celery import app as celery_app
import pymysql

#告诉Django 用pymysql代替MySQLDB
pymysql.install_as_MySQLdb()
