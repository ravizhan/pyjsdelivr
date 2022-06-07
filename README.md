# pyjsdelivr
![GitHub](https://img.shields.io/github/license/ravizhan/pyjsdelivr)
![GitHub Repo stars](https://img.shields.io/github/stars/ravizhan/pyjsdelivr)
![GitHub top language](https://img.shields.io/github/languages/top/ravizhan/pyjsdelivr)
![GitHub last commit](https://img.shields.io/github/last-commit/ravizhan/pyjsdelivr)
## 介绍
一个用Python实现的jsdelivr

从此不再受制于cdn.jsdelivr.net

演示站点: https://cdn.ravi.cool

**仍处于测试阶段，请勿用于生产环境**

## 特点
- [x] 基本兼容cdn.jsdelivr.net
- [x] 黑名单功能
- [x] 内容审核功能
- [x] 本地存储
- [x] S3云存储

## 功能对比

|    功能     | pyjsdelivr | cdn.jsdelivr.net |
|:---------:|:----------:|:----------------:|
|  github   |     ✔      |        ✔         |
|    npm    |     ✔      |        ✔         |
| wordpress |     ❌      |        ✔         |
|   文件压缩    |     ✔      |        ✔         |
|   文件合并    |     🔨     |        ✔         |

## 部署方法
### 拉取代码
```bash
git clone https://github.com/ravizhan/pyjsdelivr
```
### 安装依赖
```
cd pyjsdelivr
pip3 install ./requirements.txt
```
注意：如果需要文件压缩功能则还需安装`nodejs`，`npm`

安装方法自行搜索，然后安装`uglify-js` `clean-css-cli`模块
```
npm install uglify-js clean-css-cli -g
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
    "provider": "", //baidu/huaiwei对应为百度华为内容审核服务，为空则不开启
    "baidu_APP_ID": "",
    "baidu_APP_KEY": "",
    "baidu_SECRET_KEY": "",
    "huawei_AK": "",
    "huawei_SK": "",
    "huawei_region": "" //如cn-north-1
  },
  "storage": { //存储位置
    "location":"", // local/S3 对应为本地和S3存储,不存留空即可
    "local_dir":"/data/", // 改为本地存储地址
    "ACCESS_KEY":"",
    "SECRET_KEY":"",
    "endpoint_url":"" // 如https://s3.cn-north-1.jdcloud-oss.com
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
包含附加条款的[MIT](https://github.com/ravizhan/pyjsdelivr/blob/main/LICENSE)协议。

附加条款：
1. 不得修改或移除本程序所显示的版权声明信息(包括但不限于Response headers,首页footer)。