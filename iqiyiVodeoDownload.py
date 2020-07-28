import requests
import json
import os
from urllib import request
import re
import base64
import shutil
import sys


def downloadsVideoMethod():
    headers = {
        "Referer": "https://www.8090g.cn/jiexi/?url=" + aqy_url,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.61",
        "Sec-Fetch-Dest": "iframe",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
        "Host": "8090.winzoo.cn"
    }
    target = "http://8090.winzoo.cn/jiexi/?url=" + aqy_url
    # 尽量模仿浏览器访问接口
    req = requests.session().get(url=target, headers=headers, verify=False)
    req.encoding = "utf-8"
    # html中截取 {'url':'https://www.iqiyi.com/v_19rrz2aweg.html',
    # 'referer':'aHR0cHM6Ly93d3cuODA5MGcuY24vamlleGkvP3VybD1odHRwczovL3d3dy5pcWl5aS5jb20vdl8xOXJyejJhd2VnLmh0bWw=',
    # 'ref':form,'time':'1594721051','type':'','other':y.encode(other_l),'ref':form,'ios':''}
    apiPhpResp = re.findall('"api.php",(.+),function\(data\){if\(data.code=="200"\)', req.text)
    if apiPhpResp is None:
        print("获取referer 失败 获取数据为： ", req.text)
        return
    param = apiPhpResp[0]

    referer = param[param.index("'referer':'") + 11:param.index("','ref'")]
    other_href = "https://8090.winzoo.cn/jiexi/?url=" + aqy_url
    other = base64.b64encode(other_href[0: other_href.index('=') + 1].encode())
    data = {
        "url": aqy_url,
        "referer": referer,
        "ref": 0,
        "time": "1594376655",
        "type": "",
        "other": other,
        "ios": ""
    }
    # 获取.m3u8 路径
    video_url = "https://8090.winzoo.cn/jiexi/api.php"
    resp = requests.post(url=video_url, data=data, verify=False)
    # 因为值是字符串，所以这里把字符串转换为字典
    resp_param = json.loads(resp.text)
    type = resp_param["type"]
    if type == "false":
        print("获取路径失败， 失败路径为：" + resp_param)
    elif type == "mp4":
        print("mp4: ", resp_param["url"])
        MP4Url = resp_param["url"]
        request.urlretrieve(url=MP4Url, filename=mp4_save_path, reporthook=Schedule)
    else:
        file_path = "http:" + resp_param["url"]
        fileLoad(file_path=file_path, save_dir=save_dir, file_name=file_name)


def fileLoad(file_path, save_dir, file_name=None):
    """
    通过.m3u8 路径获取.ts文件,且写入一个自定义的ts文件中。最后转换为.mp4文件
    :param file_path: .m3u8文件
    :param save_dir: .mp4文件存储路径
    :param file_name .mp4文件名称
    :return:  包含TS链接的文件
    """
    if file_name is None or file_name == "":
        file_name = file_path.split("/")[-1]

    url_list = file_path.split("/")
    ts_referer = url_list[0] + "//" + url_list[2]

    ts_save_path = os.path.join(save_dir, "%s.ts" % file_name)
    print("save_path: ", ts_save_path)
    print("视频下载中.....")
    # m3u8下载
    m3u8_list_path = getTsList(file_path)
    for line in m3u8_list_path:
        ts_url = str(line.decode("utf-8")).strip()
        if not ".ts" in ts_url:
            continue
        else:
            writeTs(ts_url, ts_save_path, ts_referer)
        # ts 转mp4
    shutil.move(ts_save_path, mp4_save_path)
    print("\n Successfully downloaded")


def getTsList(m3u8_path):
    """
    通过.m3u8 路径获取.ts文件
    :param m3u8_path:  .m3u8路径
    :return:
    """
    try:
        return request.urlopen(m3u8_path)
    except Exception as e:
        print("\033[1;31m getTsList error. url is (%s) reason is :\033[0m" % m3u8_path, e)


def writeTs(url, save_path, referer):
    """
    将.ts文件写入save_path中
    :param url: .ts文件
    :param save_path:  自定义文件路径
    :param referer:  referer
    :return:
    """
    headers = {
        "Referer": referer,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.61",
    }
    try:
        resp = requests.get(url, headers=headers)
        with open(save_path, mode="ab") as f:
            f.write(resp.content)
            f.flush()
    except Exception as e:
        print("\033[1;31m getTsList error. url is (%s) reason is :\033[0m" % url, e)

def Schedule(a, b, c):
    per = 100.0 * a * b / c
    if per > 100:
        per = 1
    sys.stdout.write("\r>> downloading...  " + "%.2f%% 已经下载的大小:%ld 文件大小:%ld" % (per, a * b, c) + '\r')
    sys.stdout.flush()

if __name__ == "__main__":
    # 爱奇艺视频路径
    aqy_url = "https://www.iqiyi.com/v_19rr9a6m6w.html"
    file_name = "冰河世纪2"
    save_dir = "G:/ProjectPy/file/"
    mp4_save_path = os.path.join(save_dir, "%s.mp4" % file_name)
    downloadsVideoMethod()
