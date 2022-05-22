import base64
import json
import hashlib
from threading import local
import time
from aip import AipContentCensor
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkmoderation.v2.region.moderation_region import ModerationRegion
from huaweicloudsdkmoderation.v2 import ModerationClient, RunImageModerationRequest, ImageDetectionReq
import pymysql
import pymysql.cursors
from pymysql import escape_string


class DB:
    def __init__(self):
        self.conn = None
        with open("./config.json") as f:
            self.config = json.loads(f.read())["mysql"]
        self.connect()

    def connect(self):
        self.conn = pymysql.connect(
            host=self.config["host"],
            user=self.config["user"],
            password=self.config["password"],
            db=self.config["database"],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            port=self.config["port"],
            autocommit=True
        )

    def query(self, sql):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except pymysql.OperationalError:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql)
        return cursor.fetchall()


db = DB()


def img_scan(content: bytes,file: str):
    with open("./config.json") as f:
        config = json.loads(f.read())["img_scan"]
    hash = hashlib.sha256(content).hexdigest()
    sql = f"SELECT * FROM `blacklist` WHERE 'hash'='{hash}'"
    res = db.query(sql)
    if len(res) != 0:
        return False
    if config["provider"] == "":
        return True
    if config["provider"] == "baidu":
        try:
            client = AipContentCensor(config["baidu_APP_ID"], config["baidu_APP_KEY"], config["baidu_SECRET_KEY"])
            result = client.imageCensorUserDefined(content)
            if result["conclusion"] == "合规":
                return True
            else:
                detail = []
                for i in result["data"]:
                    detail.append(i["msg"])
                sql = f"INSERT INTO `blacklist` VALUES ('{file}','{hash}','{detail}','{str(round(time.time()))}')"
                db.query(sql)
                return False
        except Exception as e:
            return str(e)

    if config["provider"] == "huawei":
        credentials = BasicCredentials(config["huawei_AK"], config["huawei_SK"])
        client = ModerationClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(ModerationRegion.value_of(config["huawei_region"])) \
            .build()
        try:
            request = RunImageModerationRequest()
            request.body = ImageDetectionReq(
                threshold=0,
                categories=["politics", "terrorism", "porn"],
                moderation_rule="default",
                image=base64.b64encode(content).decode()
            )
            response = client.run_image_moderation(request)
            if response.result.suggestion == "pass":
                return True
            else:
                detail = json.dumps(response.result.category_suggestions)
                sql = f"INSERT INTO `blacklist` VALUES ('{file}','{hash}','{escape_string(detail)}','{str(round(time.time()))}')"
                db.query(sql)
                return False
        except exceptions.ClientRequestException as e:
            print(e)
            return str(e)

def stroge_file(content: bytes,file:str):
    with open("./config.json") as f:
        config = json.loads(f.read())["stronge"]
    if config["location"] == "local":
        with open(config["location"]["local_dir"]+file,"wb") as f:
            f.write(content)
        return True
    # if config["location"] == "S3":