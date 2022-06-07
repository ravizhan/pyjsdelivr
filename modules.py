import base64
import json
import hashlib
import time
from aip import AipContentCensor
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkmoderation.v2.region.moderation_region import ModerationRegion
from huaweicloudsdkmoderation.v2 import ModerationClient, RunImageModerationRequest, ImageDetectionReq
import pymysql
import pymysql.cursors
from pymysql import escape_string
import boto3
from io import BytesIO
import os
from PIL import Image


class DB:
    """MySql相关操作"""

    def __init__(self):
        self.conn = None
        with open("./config.json") as f:
            self.config = json.load(f)["mysql"]
        self.connect()

    def connect(self):
        """连接MySql"""
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
        """数据查询"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except pymysql.OperationalError:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql)
        return cursor.fetchall()


db = DB()


def img_scan(content: bytes, file: str):
    """
    图片扫描
    :param content: 图片二进制内容
    :param file: 文件路径
    :return: True/False/str
    """
    with open("./config.json") as f:
        config = json.load(f)["img_scan"]
    content_hash = hashlib.sha256(content).hexdigest()
    sql = f"SELECT * FROM `blacklist` WHERE 'hash'='{content_hash}'"
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
                sql = f"INSERT INTO `blacklist` VALUES ('{file}','{content_hash}','{detail}','{str(round(time.time()))}')"
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
                sql = f"INSERT INTO `blacklist` VALUES ('{file}','{content_hash}','{escape_string(detail)}','{str(round(time.time()))}')"
                db.query(sql)
                return False
        except exceptions.ClientRequestException as e:
            print(e)
            return str(e)


def storage_file(content: bytes, file: str):
    """
    文件存储
    :param content: 文件二进制内容
    :param file: 文件路径
    :return: True
    """
    with open("./config.json") as f:
        config = json.load(f)["storage"]
    if config["location"] == "local":
        os.makedirs(os.path.dirname(config["local_dir"] + file), exist_ok=True)
        with open(config["local_dir"] + file, "wb") as f:
            f.write(content)
        return True
    if config["location"] == "S3":
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config["ACCESS_KEY"],
            aws_secret_access_key=config["SECRET_KEY"],
            endpoint_url=config["endpoint_url"]
        )
        s3_client.upload_fileobj(BytesIO(content), config["BUCKET_NAME"], file)
        return True


def get_file(file: str):
    """
    获取存储文件
    :param file: 文件路径
    :return: 文件二进制内容
    """
    try:
        with open("./config.json") as f:
            config = json.loads(f.read())["storage"]
        if config["location"] == "local":
            with open(config["location"]["local_dir"] + file, "rb") as f:
                content = f.read()
            return content
        if config["location"] == "S3":
            s3_client = boto3.client(
                's3',
                aws_access_key_id=config["ACCESS_KEY"],
                aws_secret_access_key=config["SECRET_KEY"],
                endpoint_url=config["endpoint_url"]
            )
            content = BytesIO()
            s3_client.download_fileobj(config["BUCKET_NAME"], file[1:], content)
            content.seek(0)
            return content.read()
    except Exception:
        return None


def compress_file(content: bytes, file_type: str):
    if file_type == "img":
        img = Image.open(BytesIO(content))
        img.convert("RGB")
        data = BytesIO()
        img.save(data, 'webp', optimize=True, quality=75)
        return data.getvalue()
    if file_type == "js":
        with open("temp.js", "w", encoding="utf-8") as f:
            f.write(content.decode())
        os.system('uglifyjs ./temp.js -o ./temp.js -c -m')
        with open("temp.js", "r", encoding="utf-8") as f:
            return f.read().encode()
    if file_type == "css":
        with open("temp.css", "w", encoding="utf-8") as f:
            f.write(content.decode())
        os.system('cleancss -o temp.css temp.css')
        with open("temp.css", "r", encoding="utf-8") as f:
            return f.read().encode()
