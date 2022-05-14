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
    config = json.loads(f.read())
db = modules.db


@app.get("/")
def index():
    with open("./index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/gh/{path:path}")
def gh(path: str):
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
    if user in config["blacklist_gh"]["user"] or repo in config["blacklist_gh"]["repo"] or file.split(".")[-1] in \
            config["blacklist_gh"]["suffix"]:
        text = "This file is in blacklist.\nPlease contact website manager for more detail."
        return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    url = config["origin"]["github"]+"%s/%s/%s/%s" % (user, repo, version, file)
    req = r.get(url)
    if req.status_code != 200:
        text = "Failed to fetch " + '/'.join([user, repo, version]) + "/" + file + "\nPealse check your enter"
        return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    if url.split(".")[-1] in ["jpg", "jpeg", "bmp", "png"]:
        res = modules.img_scan(req.content, file)
        if type(res) == str:
            text = "Something goes wrong.\nPlease contact website manager for more detail."
            return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
        if not res:
            text = "This file is in blacklist.\nPlease contact website manager for more detail."
            return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    return Response(content=req.content, headers={"content-type": req.headers["content-type"]})


@app.get("/npm/{path:path}")
def npm(path: str):
    # 路径处理
    path_split = path.split("/")
    if "@" in path_split[0]:
        package = path_split[0].split("@")[0]
        version = path_split[0].split("@")[1]
    else:
        text = "No version was specified.\nRight format: package@version/file"
        return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    filename = "/".join(path_split[1:])
    if package in config["blacklist_npm"]["package"] or filename.split(".")[-1] in config["blacklist_npm"]["suffix"]:
        text = "This file is in blacklist.\nPlease contact website manager for more detail."
        return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    url = config["origin"]["npm"]+path
    req = r.get(url)
    if req.status_code != 200:
        text = "Failed to fetch %s@%s/%s\nPealse check your enter" % (package, version, filename)
        return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    if url.split(".")[-1] in ["jpg", "jpeg", "bmp", "png"]:
        res = modules.img_scan(req.content, path)
        if not res:
            text = "This file is in blacklist.\nPlease contact website manager for more detail."
            return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
        if type(res) == str:
            text = "something goes wrong.\nPlease contact website manager for more detail."
            return Response(content=text, headers={"content-type": "text/plain; charset=utf-8"})
    return Response(content=req.content, headers={"content-type": req.headers["content-type"]})


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app")
