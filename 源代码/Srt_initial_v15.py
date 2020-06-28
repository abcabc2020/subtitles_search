# -*- coding: utf-8 -*-
import configparser
import os
def inic():
    cf = configparser.ConfigParser()
    cf['字幕文件库设置'] = {
        '字幕文件文件夹(逗号隔开)':''
    }
    cf['程序设置']={
        '需要字幕后缀(逗号隔开)':'ass,srt,smi,ssa,sub',
        '是否为影片建立单独文件夹':'是',
        '字幕是否拷贝(填否则进行剪切移动)': '是'
    }
    f = open('点击设置字幕匹配软件配置.ini', 'w', encoding='utf-8')
    cf.write(f)
    f.close()
if __name__=="__main__":
    inic()