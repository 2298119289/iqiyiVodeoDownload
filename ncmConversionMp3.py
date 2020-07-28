import os
import re
import shutil
from pathlib import Path


def findNcmFile():
    """
    查找ncm文件且转换
    :return:
    """
    dir_list = os.listdir(musicFilePath)
    compileFile = re.compile(".ncm")
    for cur_file in dir_list:
        matchFile = compileFile.search(cur_file)
        if matchFile:
            ncmFilePath = os.path.join(musicFilePath, cur_file)
            conversionFile(ncmFilePath)


def conversionFile(filePath):
    """
    调用脚本转换文件格式
    :param filePath:
    :return:
    """
    print("ncmUrl : ", filePath)
    cmd = mainPath + " \"" + filePath + "\""
    print(cmd)
    o = os.popen(cmd)
    print("o：", o.read())


def removeNcmFile():
    """
    转移ncm文件
    :return:
    """
    if not os.path.exists(ncmFilePath):
        print("文件夹不存在, 创建文件")
        os.makedirs(ncmFilePath)
    dir_list = os.listdir(musicFilePath)
    compileFile = re.compile(".ncm")
    for cur_file in dir_list:
        matchFile = compileFile.search(cur_file)
        if matchFile:
            source = os.path.join(musicFilePath, cur_file)
            destination = os.path.join(ncmFilePath, cur_file)
            try:
                shutil.move(source, destination)
            except Exception as e:
                continue
            print("已转移, 文件：", cur_file)


if __name__ == "__main__":
    musicFilePath = "F:/CloudMusic"
    ncmFilePath = "F:/CloudMusic/ncmFile"
    mainPath = "E:\\installationPackage\\ncmdump-master\\ncmdump-master\\main.exe"
    removeNcmFile()
