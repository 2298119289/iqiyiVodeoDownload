import os
import shutil
import requests
import json
import re
import threading
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

savePath = "F:\知乎电脑壁纸"
deleteFiles = "F:\deleteFile"
zhiHuPath = "https://www.zhihu.com/api/v4/search_v3?t=general&q=%E7%94%B5%E8%84%91%E5%A3%81%E7%BA%B8&correction=1&offset=0&limit=20&lc_idx=0&show_all_topics=0"
imgSrcList = set()
exifDate = {}

headers = {"x-zse-83": "3_2.0",
           "x-zse-86": "1.0_a0FBk4U8bTtpng2qy9N0bQH8nqFYHB20mLF0Q0uyHgtx",
           "referer": "https://www.zhihu.com/search?type=content&q=%E7%94%B5%E8%84%91%E5%A3%81%E7%BA%B8",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
           "cookie": "_zap=997db400-25c9-4655-bd21-22427e29f1fa; _xsrf=9ee6176d-98ea-4c5d-84fb-15d4772fd0e7; d_c0=\"ADAYUSpa6hCPTpdDdXjszMmSJiRGV2lgGc8=|1583385017\"; _ga=GA1.2.1724098359.1583385019; __utmc=51854390; __utmv=51854390.100--|2=registration_date=20170928=1^3=entry_date=20170928=1; z_c0=\"2|1:0|10:1593488291|4:z_c0|92:Mi4xUURnUUJnQUFBQUFBTUJoUktscnFFQ1lBQUFCZ0FsVk5vd0hvWHdDbmpKbVFHVmYwdk5IalFoeFhOcGFPRVZxLUR3|7650e57cec58e3cfac8dd14176434ebcf30429938d5fe352d588a33c47dbde85\"; __utma=51854390.1724098359.1583385019.1590749590.1594103937.2; __utmz=51854390.1594103937.2.2.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/question/398673970; tst=h; tshl=; q_c1=8fcf2d5c25fb4d159738962a9db20efa|1606102188000|1583829972000; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1606465692,1606709785,1606818482,1606891718; SESSIONID=EcITAJ1oB61cpFl88hVvDu9Nen56bYgeibazfoooA9Y; JOID=UlkTB0kIkYtGu-65Kgxy3NY89jQ9TPXAFPilj0dIpr0nzarUFV7WSB246LwuxWwVPl079wfxA2aHgYEAVAZ4LBs=; osd=VlwXAUMMlI9Aseq8Lgp42NM48D45SfHGHvygi0FCorgjy6DQEFrQQhm97LokwWkROFc_8gP3CWKChYcKUAN8KhE=; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1606894364; KLBRSID=cdfcc1d45d024a211bb7144f66bda2cf|1606894368|1606891718"}


def searchFile():
    """
    获取文件集合
    :return: void
    """
    url = requests.get(zhiHuPath, headers=headers)
    UrlContent = url.content
    obj = json.loads(UrlContent)
    objs = obj["data"]
    for i in range(0, len(objs)):
        if "object" not in objs[i]:
            continue
        data = objs[i]["object"]
        if "content_list" in data:
            content_list = data["content_list"]
            # comment_count 评论数
            # voteup_count 点赞数
            # updated_time 更新时间
            # 排序逻辑,点赞数最多
            if len(content_list) > 1:
                content_listSort = sorted(content_list, key=lambda x: x["voteup_count"], reverse=True)
                # 转JSON
                for i in range(0, len(content_listSort)):
                    if "content" in data:
                        content = content_listSort[i]["content"]
                        resolveContent(content)
        elif "content" in data:
            content = data["content"]
            resolveContent(content)
        else:
            print("no content_list, continue.")


def resolveContent(content):
    """
    解析出图片路径
    :param content: 需要解析的内容
    :return: void
    """
    findallSrc = re.findall(r'data-original="(.*?)"', content, re.M | re.I)
    if findallSrc:
        for j in range(len(findallSrc)):
            imgSrcList.add(findallSrc[j])
    else:
        print("no data")


def downloadImages():
    """
    多线程下载文件
    :return: void
    """
    imgSrcListSize = len(imgSrcList)
    print("imgSrcListSize: ", imgSrcListSize)
    executor = ThreadPoolExecutor(max_workers=80)
    all_task = [executor.submit(downloadImage, imgSrc) for imgSrc in imgSrcList]
    # 阻塞主线程，等待线程池中线程运行完毕
    wait(all_task, return_when=ALL_COMPLETED)
    print("executor end")


def downloadImage(src):
    """
    下载文件
    :param src: 文件路径
    :return: void
    """
    print("当前线程信息 %s" % threading.currentThread())
    match = re.search(r'\w+://[^/:]+/([^#]*)', src, re.M | re.I)
    if match:
        imageName = match.group(1)
        response = requests.get(src, headers)
        with open(savePath + "\\" + imageName, mode='wb+') as f:
            f.write(response.content)
            f.flush()
        print("当前线程信息 %s" % threading.currentThread())
    else:
        print("no data")



def getImgDetail():
    """
    将不符合要求的文件移动到, deleteFiles文件夹
    :return: void
    """
    files = os.listdir(savePath)
    print(len(files))
    for i in range(len(files)):
        fileName = files[i]
        filePath = savePath + '/' + fileName
        # 不符合的图片将移动到deleteFiles文件夹
        fileMovePath = deleteFiles + '/' + fileName
        try:
            imageFile = Image.open(filePath)
            imageFile.close()
            # 符合条件，根据自己情况修改
            if (imageFile.width < 1920 or imageFile.height < 1080):
                shutil.move(filePath, fileMovePath)
        except Exception as e:
            print(e)
            # 因为还有部分图片下载打不开，也有可能是下载失败。
            # 所以还需要在抓取到异常的时候移动一下不能打开的图片
            shutil.move(filePath, fileMovePath)
            continue


def main():
    searchFile()
    downloadImages()
    getImgDetail()


if __name__ == "__main__":
    main()
