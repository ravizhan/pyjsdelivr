# pyjsdelivr
## 介绍
一个用Python实现的jsdelivr

从此不再受制于cdn.jsdelivr.net

演示站点: https://cdn.ravi.cool

**仍处于测试阶段，请勿部署**

## 功能
- [x] 基本兼容cdn.jsdelivr.net
- [x] 黑名单功能
- [x] 内容审核功能
- [x] 本地存储
- [ ] S3云存储
## 部署方法
### 拉取代码
```bash
git clone https://github.com/ravizhan/pyjsdelivr
cd pyjsdelivr
pip3 install ./requirements.txt
```
### 修改配置文件
对照下方，编辑 `config.example.json`
**并重命名为 `config.josn`**
```json
{
  "origin":{ // 可改为自建源
    "github":"https://raw.githubusercontent.com/",
    "npm":"https://unpkg.com/"
  },
  "blacklist_gh": { //github黑名单
    "repo": ["xxx","xx"], //仓库黑名单
    "user": [], //用户黑名单
    "suffix": [] //后缀黑名单
  },
  "blacklist_npm": { //npm黑名单
    "package": [], //包黑名单
    "suffix": [] //后缀黑名单
  },
  "img_scan": { //内容审核服务
    "povider": "", //baidu/huaiwei对应为百度华为内容审核服务，为空则不开启
    "baidu_APP_ID": "",
    "baidu_APP_KEY": "",
    "baidu_SECRET_KEY": "",
    "huawei_AK": "",
    "huawei_SK": "",
    "huawei_region": "" //如cn-north-1
  },
  "stronge": { //存储位置
    "location":"", // local/S3 对应为本地和S3存储
    "local_dir":"/data/", // 改为本地存储地址
    "ACCESS_KEY":"",
    "SECRET_KEY":"",
    "endpoint_url":"", // 如https://s3.cn-north-1.jdcloud-oss.com
  },
  "mysql": { //mysql连接信息
    "host": "",
    "port": "",
    "user": "",
    "password": "",
    "database": ""
  }
}
```
### 启动
二选一即可
```bash
python3 ./main.py
```
```bash
uvicorn main:app
```
建议配合nginx反代使用并开启缓存

## 开源协议
依据 [MIT license](https://github.com/ravizhan/pyjsdelivr/blob/main/LICENSE) 开源，请自觉遵守
