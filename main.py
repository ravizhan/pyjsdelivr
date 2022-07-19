import json
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse
import requests
import modules
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
)
r = requests.session()
with open("./config.json") as f:
    config = json.load(f)
db = modules.db


@app.middleware("http")
async def process(request: Request, call_next):
    """中间件处理请求"""
    response = await call_next(request)
    response.headers["X-Powered-by"] = "ravizhan/pyjsdelivr"
    response.headers["Content-Disposition"] = "inline"
    return response


@app.get("/")
def index():
    """首页"""
    with open("./index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/gh/{path:path}")
def gh(path: str):
    """处理github请求"""
    # 路径处理
    path_split = path.split("/")
    user = path_split[0]
    if "@" in path_split[1]:
        repo = path_split[1].split("@")[0]
        version = path_split[1].split("@")[1]
    else:
        repo = path_split[1]
        version = "master"
    file = "/".join(path_split[2:])
    # 判断黑名单
    if user in config["blacklist_gh"]["user"] or repo in config["blacklist_gh"]["repo"] or file.split(".")[-1] in \
            config["blacklist_gh"]["suffix"]:
        text = "This file is in blacklist.\nPlease contact website manager for more detail."
        return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    # 文件存储
    url = str(config["origin"]["github"] + "%s/%s/%s/%s" % (user, repo, version, file))
    if ".".join(url.split(".")[-2:]) in ["jpg.webp", "jpeg.webp", "bmp.webp", "png.webp"]:
        url = url[:-5]
    if config["storage"]["location"] in ["local", "S3"]:
        content = modules.get_file("/gh/" + path)
        if content is not None:
            return Response(content=content)
    req = r.get(url)
    if req.status_code != 200:
        if url.endswith(("min.js", "min.css")):
            req = r.get(url.replace("min.", ""))
            if req.status_code == 200:
                # 文件压缩
                content = modules.compress_file(req.content, url.split(".")[-1])
                if config["storage"]["location"] in ["local", "S3"]:
                    modules.storage_file(req.content, "gh/" + path)
                return Response(content=content, headers={"content-type": req.headers["content-type"]})
        text = "Failed to fetch " + '/'.join([user, repo, version]) + "/" + file + "\nPlease check your enter"
        return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    # 图片扫描
    if "image" in req.headers["content-type"]:
        res = modules.img_scan(req.content, "gh/" + path)
        if type(res) is str:
            text = "Something goes wrong.\nPlease contact website manager for more detail."
            return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
        if not res:
            text = "This file is in the blacklist.\nPlease contact website manager for more detail."
            return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    # 图片压缩
    if ".".join(path.split(".")[-2:]) in ["jpg.webp", "jpeg.webp", "bmp.webp", "png.webp"]:
        content = modules.compress_file(req.content, "img")
        if config["storage"]["location"] in ["local", "S3"]:
            modules.storage_file(content, "gh/" + path)
        return Response(content=content, headers={"content-type": req.headers["content-type"]})
    if config["storage"]["location"] in ["local", "S3"]:
        modules.storage_file(req.content, "gh/" + path)
    return Response(content=req.content, headers={"content-type": req.headers["content-type"]})


@app.get("/npm/{path:path}")
def npm(path: str):
    """处理npm请求"""
    # 路径处理
    path_split = path.split("/")
    if "@" in path_split[0]:
        package = path_split[0].split("@")[0]
        version = path_split[0].split("@")[1]
    else:
        text = "No version was specified.\nRight format: package@version/file"
        return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    filename = "/".join(path_split[1:])
    # 判断黑名单
    if package in config["blacklist_npm"]["package"] or filename.split(".")[-1] in config["blacklist_npm"]["suffix"]:
        text = "This file is in blacklist.\nPlease contact website manager for more detail."
        return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    # 文件存储
    url = config["origin"]["npm"] + path
    if ".".join(url.split(".")[-2:]) in ["jpg.webp", "jpeg.webp", "bmp.webp", "png.webp"]:
        url = url[:-5]
    if config["storage"]["location"] in ["local", "S3"]:
        content = modules.get_file("npm/" + path)
        if content is not None:
            return Response(content=content)
    req = r.get(url)
    if req.status_code != 200:
        if url.endswith(("min.js", "min.css")):
            req = r.get(url.replace("min.", ""))
            if req.status_code == 200:
                # 文件压缩
                content = modules.compress_file(req.content, url.split(".")[-1])
                if config["storage"]["location"] in ["local", "S3"]:
                    modules.storage_file(req.content, "npm/" + path)
                return Response(content=content, headers={"content-type": req.headers["content-type"]})
        text = "Failed to fetch %s@%s/%s\nPlease check your enter" % (package, version, filename)
        return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    # 图片扫描
    if "image" in req.headers["content-type"]:
        res = modules.img_scan(req.content, "/npm/" + path)
        if type(res) is str:
            text = "something goes wrong.\nPlease contact website manager for more detail."
            return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
        if not res:
            text = "This file is in the blacklist.\nPlease contact website manager for more detail."
            return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    # 图片压缩
    if ".".join(path.split(".")[-2:]) in ["jpg.webp", "jpeg.webp", "bmp.webp", "png.webp"]:
        content = modules.compress_file(req.content, "img")
        if config["storage"]["location"] in ["local", "S3"]:
            modules.storage_file(content, "npm/" + path)
        return Response(content=content, headers={"content-type": req.headers["content-type"]})
    if config["storage"]["location"] in ["local", "S3"]:
        modules.storage_file(req.content, "npm/" + path)
    return Response(content=req.content, headers={"content-type": req.headers["content-type"]})


@app.get("/combine/{path:path}")
def combine(path: str):
    paths = path.split(",")
    result = b""
    for _path in paths:
        if not _path.endswith(("js", "css")):
            text = "The files must be js or css."
            return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
        if _path.startswith("gh"):
            _path = _path[3:]
            # 路径处理
            path_split = _path.split("/")
            user = path_split[0]
            if "@" in path_split[1]:
                repo = path_split[1].split("@")[0]
                version = path_split[1].split("@")[1]
            else:
                repo = path_split[1]
                version = "master"
            file = "/".join(path_split[2:])
            # 判断黑名单
            if user in config["blacklist_gh"]["user"] or repo in config["blacklist_gh"]["repo"] or file.split(".")[
                -1] in \
                    config["blacklist_gh"]["suffix"]:
                text = "This file is in blacklist.\nPlease contact website manager for more detail."
                return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
            # 文件存储
            url = str(config["origin"]["github"] + "%s/%s/%s/%s" % (user, repo, version, file))
            if ".".join(url.split(".")[-2:]) in ["jpg.webp", "jpeg.webp", "bmp.webp", "png.webp"]:
                url = url[:-5]
            if config["storage"]["location"] in ["local", "S3"]:
                content = modules.get_file("/gh/" + _path)
                if content is not None:
                    result += b"\n\n" + content
                    continue
            req = r.get(url)
            if req.status_code != 200:
                if url.endswith(("min.js", "min.css")):
                    req = r.get(url.replace("min.", ""))
                    if req.status_code == 200:
                        # 文件压缩
                        content = modules.compress_file(req.content, url.split(".")[-1])
                        if config["storage"]["location"] in ["local", "S3"]:
                            modules.storage_file(req.content, "gh/" + _path)
                        result += b"\n\n" + content
                        continue
                text = "Failed to fetch " + '/'.join([user, repo, version]) + "/" + file + "\nPlease check your enter"
                return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
            result += b"\n\n" + req.content
            continue
        if _path.startswith("npm"):
            _path = _path[4:]
            # 路径处理
            path_split = _path.split("/")
            if "@" in path_split[0]:
                package = path_split[0].split("@")[0]
                version = path_split[0].split("@")[1]
            else:
                text = "No version was specified.\nRight format: package@version/file"
                return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
            filename = "/".join(path_split[1:])
            # 判断黑名单
            if package in config["blacklist_npm"]["package"] or filename.split(".")[-1] in config["blacklist_npm"][
                "suffix"]:
                text = "This file is in blacklist.\nPlease contact website manager for more detail."
                return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
            # 文件存储
            url = config["origin"]["npm"] + _path
            if ".".join(url.split(".")[-2:]) in ["jpg.webp", "jpeg.webp", "bmp.webp", "png.webp"]:
                url = url[:-5]
            if config["storage"]["location"] in ["local", "S3"]:
                content = modules.get_file("npm/" + _path)
                if content is not None:
                    result += b"\n\n" + content
                    continue
            req = r.get(url)
            if req.status_code != 200:
                if url.endswith(("min.js", "min.css")):
                    req = r.get(url.replace("min.", ""))
                    if req.status_code == 200:
                        # 文件压缩
                        content = modules.compress_file(req.content, url.split(".")[-1])
                        if config["storage"]["location"] in ["local", "S3"]:
                            modules.storage_file(req.content, "npm/" + _path)
                        result += b"\n\n" + req.content
                        continue
                text = "Failed to fetch %s@%s/%s\nPlease check your enter" % (package, version, filename)
                return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
            result += b"\n\n" + req.content
            continue
    return Response(content=result, headers={
        "content-type": "application/javascript; charset=utf-8" if path.endswith("js") else "text/css; charset=utf-8"})


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app")
