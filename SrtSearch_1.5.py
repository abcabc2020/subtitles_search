# -*- coding: utf-8 -*-
import pandas as pd
import time
import re
import sys
import os
from queue import Queue
import time
import xml.etree.ElementTree as ET
import configparser
import Srt_initial_v15
import win32file
import shutil
import tkinter as tk
from tkinter import filedialog
######################################################
print('作者：abc2020,SrtSearch_v1.5 如果有问题请发邮箱')
print('注意：使用notepad++编辑配置文件！')
print("请确认你的 '点击设置字幕匹配软件配置.ini'文件配置选项！按输入数字 1 继续：")
strn=input("请输入：");
if int(strn)!=1:
    print('看来你还没有准备好，程序结束。')
    os.system('pause')
    sys.exit(1)
######################################################

#Filepath = filedialog.askopenfilename() #获得选择好的文件

#StartNum=int (config.get("爬取设置","开始页面(最小为1)"))
Consider_done=1    #考虑之前汉化过的问题
#CsvPath=r'./98_Data/Csv_data/98CTest.csv'
#FilePath=[]
SrtPath=[]
#txtPath=r'./transformjournal.txt'
AllFileName=Queue()#记录更改文件名的
localtime = time.localtime(time.time())
#dirnameC=0
write1=0
FinishDirName='分配完成'
SrtData = pd.DataFrame(columns=['Code', '字幕路径'])
Log=pd.DataFrame(columns=['Code', '字幕匹配说明','是否有匹配字幕','匹配字幕路径','匹配字幕数','影片路径'])
#movieData=pd.DataFrame(columns=['Code', '影片路径'])
movieData=Queue()
#print ("本地时间为 :", localtime)
moviepat='\\.mp4|\\.avi|\\.wmv|\\.mkv|\\.rmvb'
makedir=0
finishMovieDir=''
movieMovie=1
cmode='move'
def configpathdeal(apath):
    if apath == '':
        print('待处理列表为空！程序退出！')
        os.system('pause')
        sys.exit(1)
    fp = re.split('[,，]', apath)  # 多个分隔符，处理中文逗号，,
    for i in range(len(fp)):
        fp[i] = fp[i].strip()  # 去空格
    return fp
if not os.path.isfile('点击设置字幕匹配软件配置.ini'):
    print('点击设置字幕匹配软件配置.ini not exists!')
    Srt_initial_v15.inic()
    #os.system("TR_initial_config.exe")
    print('new 点击设置字幕匹配软件配置.ini!')
config=configparser.ConfigParser()
config.read('点击设置字幕匹配软件配置.ini',encoding='utf-8')
#Consider_done=1 if config.get("程序设置","是否考虑以前汉化标识")=='是' else 0
#Apath=config.get("路径设置","待处理文件路径(逗号隔开)")
Spath=config.get("字幕文件库设置","字幕文件文件夹(逗号隔开)")
SrtPath=configpathdeal(Spath)
#FilePath=configpathdeal(Apath)
cmode='copy' if config.get("程序设置","字幕是否拷贝(填否则进行剪切移动)")=='是' else 'move'
Srtpat=config.get("程序设置","需要字幕后缀(逗号隔开)")#ass、srt、smi、ssa、sub
if Srtpat=='':
    print('你的识别格式为空，将以默认的.srt格式识别，是否继续？按输入数字 1 继续：')
    strn = input("请输入：");
    if int(strn) != 1:
        print('看来你还没有准备好，程序结束。')
        os.system('pause')
        sys.exit(1)
    Srtpat='\\.srt'

else:
    Srtpat=re.split('[,，]',Srtpat)
    for i in range(len(Srtpat)):
        Srtpat[i]=Srtpat[i].strip()
        if not re.search('\.',Srtpat[i]):
            print("错误！识别影片后缀模板没有'.'!自动添加'.'！")
            Srtpat[i]='.'+Srtpat[i]
            Srtpat[i]='\\'+Srtpat[i]
    Srtpat="|".join(Srtpat)
#CsvPath=config.get("程序设置","程序使用数据库路径")
#dirnameC=1 if config.get("程序设置","是否更改上一层文件目录名字(需要保证一个文件夹下一个视频)")=='是' else 0
makedir=1 if config.get("程序设置","是否为影片建立单独文件夹")=='是' else 0
######################################################
"""
try:
    Data=pd.read_csv(CsvPath,encoding = 'utf_8_sig')
except Exception as e:
    print('Wrong at read data in Pandas!')
    os.system('pause')
    sys.exit(1)
print('import data success!')
"""
def FindMovFiles(path1):#递归找到所有文件
    #print('读入影片文件路径')
    abspath=path1
    abspath = os.path.abspath(path1)
    filelist = os.listdir(abspath)
    #total_num = len(filelist)
    for file in filelist:
        filepath=os.path.join(abspath,file)
        if os.path.isdir(filepath):
            if os.path.split(filepath)[1]!=FinishDirName:
                FindMovFiles(filepath)
        else:
            ext=os.path.splitext(file)[1]
            if re.search(moviepat,ext):
                code=CodeManifest(file)
                if code !='':
                    ChineseS = '-c|-C|㊥'
                    chinese = ''
                    if re.search(ChineseS, file):  # 是否中文
                        chinese = '是'
                    else:
                        chinese = '否'
                    i,splist=srtSearch(code)
                    d=[code,filepath,i,splist,chinese]#番号，电影路径，字幕数量，字幕列表,是否中文
                    movieData.put(d)

        #movieData=movieData.append({'Code':code,'影片路径':filepath},ignore_index=True)
def FindSrtFiles(path1):#递归找到所有文件
    print('读入字幕文件路径')
    abspath=path1
    abspath = os.path.abspath(path1)
    filelist = os.listdir(abspath)
    #total_num = len(filelist)
    global SrtData
    for file in filelist:
        filepath=os.path.join(abspath,file)
        if os.path.isdir(filepath):
            if os.path.split(filepath)[1]!=FinishDirName:
                FindSrtFiles(filepath)
        else:
            ext=os.path.splitext(file)[1]
            bb=re.search(Srtpat,ext)
            if bb:
                code=CodeManifest(file)
                if code !='':
                    SrtData=SrtData.append({'Code':code,'字幕路径':filepath},ignore_index=True)
def srtSearch(code):
    #data2 = data.loc[data['Code'] == 'HND-792'].reset_index(drop=True, inplace=False).at[0, 'Title']
    data_ten=SrtData.loc[SrtData['Code']==code]
    i=len(data_ten.index)
    spathlist=[]
    if i==0:
        print('dont find this code!')
        return 0,[]
    for ii in range(i):
        spathlist.append(data_ten['字幕路径'].iloc[ii])
    return i,spathlist
def CodeManifest(oldname):
    if oldname.find('-cd1')!=-1 or oldname.find('-cd2')!=-1:
        return ''
    code=re.search("[a-zA-Z]{2,5}[-_]?\d{2,4}",oldname)#提取番号
    if code:
        code=code.group()
        code=code.upper()#全部大写
    else:
        print("在{}匹配不到番号！".format(oldname))
        return ''#普通电影
    return code
def checkSrt(path1,mcode):#检查文件夹中是否已经存在字幕
    print('检查电影番号:{} 的文件夹中是否有对应字幕'.format(mcode))
    abspath = path1
    abspath = os.path.abspath(path1)
    filelist = os.listdir(abspath)
    for file in filelist:
        filepath = os.path.join(abspath, file)
        if os.path.isdir(filepath):
            flag,path=checkSrt(filepath,mcode)
            if flag==1:
                return flag,path
        else:
            ext = os.path.splitext(file)[1]
            if re.search(Srtpat, ext):
                code = CodeManifest(file)
                if code != '':
                    if code==mcode:
                        return 1,filepath
    return 0,''
def checkMov(path1):#看看文件夹中是否只有一部影片
    # print('读入影片文件路径')
    abspath = path1
    abspath = os.path.abspath(path1)
    filelist = os.listdir(abspath)
    # total_num = len(filelist)
    n=0
    for file in filelist:
        filepath = os.path.join(abspath, file)
        if os.path.isdir(filepath):
            d=checkMov(filepath)
            n=n+d
        else:
            ext = os.path.splitext(file)[1]
            if re.search(moviepat, ext):
                code = CodeManifest(file)
                if code != '':
                    n=n+1
    return n
            # movieData=movieData.append({'Code':code,'影片路径':filepath},ignore_index=True)
def writeSrtTxt(txtpath,srtlist,code,nowsrtpath):
    with open(txtpath, 'a+', encoding='utf-8')as f:
        f.write('****************{} 任务****************\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        f.write('{}:现有字幕原路径{}:'.format(code,nowsrtpath))
        f.write('\n总字幕路径:\n')
        for i in srtlist:
            f.write(i)
            f.write('\n')

def chooseSrt():#字幕分配处理
    global Log
    while not movieData.empty():
        l=movieData.get()
        code=l[0]
        mpath=l[1]
        num=l[2]
        spath=l[3]
        c=l[4]
        srtpath='-'
        srtmatch='是' if num>0 else '否'
        old=os.path.split(mpath)
        name=os.path.split(os.path.splitext(mpath)[0])[1]
        dirpath=old[0]
        attach=''
        movsum=0
        if c=='是':
            print(code,'已经是中文字幕影片！')
            attach='已经是中文字幕影片,有标识符'
        else:
            flag, oldsrtpath = checkSrt(dirpath, code)
            if flag == 1:
                print('找到原有字幕')
                attach = '找到原有字幕'
                srtpath=oldsrtpath
                if num!=0 and write1==1:
                    tp=os.path.join(dirpath,'字幕列表(有其他字幕).txt')
                    writeSrtTxt(tp,spath,code,srtpath)
            else:
                if num==0:
                    attach='未找到字幕'
                else:
                    #####移动字幕###
                    if makedir == 1:
                        movsum=checkMov(dirpath)
                        if movsum !=1:
                            newdirpath = os.path.join(dirpath, code)
                            if not os.path.exists(newdirpath):
                                os.mkdir(newdirpath)
                            dirpath = newdirpath
                            shutil.move(mpath, dirpath)
                            mpath = os.path.join(dirpath, old[1])
                    attach = '匹配到字幕'
                    #srcpath=spath[0]
                    srtpath=spath[0]
                    srtext=os.path.splitext(srtpath)[1]
                    #srtname=os.path.split(srcpath)[1]
                    #dstpath=os.path.join(dirpath,name+srtext)
                    #shutil.copyfile(srcpath,dstpath)
                    dstpath=dirpath
                    try:
                        shutil.copy2(srtpath,dstpath)
                    except Exception as e:
                        with open(os.path.join(dstpath,'匹配失败可能是有同名影片.txt'), 'a+', encoding='utf-8')as f:
                            f.close()
                        Log = Log.append(
                            {'Code': code, '是否有匹配字幕': srtmatch, '影片路径': mpath, '匹配字幕数': num, '匹配字幕路径': srtpath,
                             '字幕匹配说明': '匹配到字幕但是因为字幕路径改变失败'}, ignore_index=True)
                        continue
                    #srtpath=os.path.join(dirpath,srtname)
                    ######移动字幕文件夹####
                    ss=os.path.split(srtpath)
                    if re.search("abc2020自提",ss[1])or re.search("自提",ss[1]) :
                        print('恭喜 找到一个作者本人自提的字幕！')

                    else:
                        finishdir=os.path.join(os.path.dirname(srtpath),FinishDirName)
                        mode=1
                        srtpath=srtdirfinish(srtpath, finishdir, cmode, mode)
                        #srtpath=os.path.join(finishdir,ss[1])
                        spath[0] = srtpath
                    #############
                    if movsum==1:
                        namelist = ['-poster.jpg', '-fanart.jpg', '.nfo']
                        for i in namelist:
                            ip=os.path.join(dirpath,name+i)
                            if os.path.exists(ip):
                                os.remove(ip)
                    if num==1:
                        tp=os.path.join(dirpath,'字幕列表.txt')
                        writeSrtTxt(tp, spath, code, srtpath)
                    else:
                        tp = os.path.join(dirpath, '字幕列表(有其他字幕).txt')
                        writeSrtTxt(tp, spath, code, srtpath)



        # Log=pd.DataFrame(columns=['Code', '是否有匹配字幕','匹配字幕路径','匹配字幕数','影片路径'])
        Log=Log.append({'Code':code,'是否有匹配字幕':srtmatch,'影片路径':mpath,'匹配字幕数':num,'匹配字幕路径':srtpath,'字幕匹配说明':attach},ignore_index=True)
def srtdirfinish(fpath,dstdir,str,mode):
    if not os.path.exists(dstdir):
        os.mkdir(dstdir)
    #dirpath=os.path.dirname(fpath)
    if str=='move':
        n=shutil.move(fpath,dstdir)
    elif str=='copy':###有问题
        if mode==1:#无单独文件夹字幕
            n=shutil.copy2(fpath,dstdir)
        elif mode==2:#自提字幕#需要在下面新建目录
            #dirpath = os.path.dirname(fpath)
            srtdirname=os.path.split(fpath)[1]
            dstdir=os.path.join(dstdir,srtdirname)
            try:
                n=shutil.copytree(fpath,dstdir)
            except Exception as e:
                print('目标文件目录已存在')
                n=dstdir
    return n
for s in SrtPath:
    FindSrtFiles(s)
print('读取字幕列表成功')
while True:
    '''打开选择文件夹对话框'''
    root = tk.Tk()
    root.withdraw()

    file_pat = filedialog.askdirectory()  # 获得选择好的文件夹
    #Filepath = filedialog.askopenfilename()  # 获得选择好的文件
    finishMovieDir=os.path.join(file_pat,'分配完成')
    if makedir==1:
        if not os.path.exists(finishMovieDir):
            os.mkdir(finishMovieDir)
    FindMovFiles(file_pat)
    print('文件夹:',file_pat,'读取成功')
    chooseSrt()
    print('字幕匹配移动完成')
    txtpath=os.path.join(file_pat,'字幕匹配日志.csv')
    txt2path=os.path.join(file_pat,'成功匹配.csv')
    t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    timeline=[t for x in range(2,len(Log.index)+2)]
    Log.insert(loc=0,column='任务时间',value=timeline)
    #with open(txtpath, 'a+', encoding='utf-8')as f:
        #f.write('****************{} 任务****************\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        #f.close()
    Log.to_csv(txtpath, mode='a', index=False, header=True, encoding='utf_8_sig')
    L1= Log.loc[Log['字幕匹配说明']=='匹配到字幕'].reset_index(drop=True,inplace=False)
    if L1.empty:
        print('{}这个文件夹没有匹配到字幕'.format(file_pat))
    L1.to_csv(txt2path, mode='a', index=False, header=True, encoding='utf_8_sig')
    print('日志写入成功')
    Log.drop(Log.index, inplace=True)
    Log.drop(columns=['任务时间'],inplace=True)
    print('字幕匹配完成，详情请查阅文件夹中的 成功匹配.csv 和 字幕替换日志.csv')
    print('按任意键继续选择文件夹匹配：')
    os.system('pause')





