# 这个项目已经停止更新，全部内容已经用Rust重写，见 [bilibili_comics_downloader](https://github.com/lihe07/bilibili_comics_downloader)

新的Issue不会再处理

# bilibili-manga-downloader
下载哔哩哔哩漫画的爬虫， 支持范围下载， 逐话导出PDF，自动合并PDF

## 项目特点
1. 支持多线程下载
2. 可自定义下载范围
3. 可以导出每一话的PDF文件
4. 自动合并PDF 并生成阅读器可读的书签

## 可执行程序

对于一般用户，建议使用打包好的可执行程序。

https://github.com/lihe07/bilibili-manga-downloader/releases/latest

## 运行环境
Python 3.x
在CMD或BASH中执行这行指令:```pip3 install -r  requirements.txt```

## 使用方法

在CMD或BASH中执行
```
python3 main.py
```
执行后按照提示输入信息

### 	1. 获取漫画ID(comicID):

​		进入漫画详情页(如图)

​		![漫画详情](/images/info.jpg "漫画详情")

​		此时的链接 manga.bilibili.com/detail/mc**25493** 中加粗部分就是漫画ID

​		这里的例子是__25493__

### 2. 付费漫画下载 SESSDATA获取
​		如果要下载付费漫画, 则需要登录自己的账号, 并输入SESSDATA

​		请在浏览器登录BiliBili漫画后, 获取cookies中的"SESSDATA"

1. 点击链接框前小锁符号
	![获取cookie](/images/getCookies1.jpg "获取cookie")
2. 点击Cookie字段
	![获取cookie](/images/getCookies2.jpg "获取cookie")
3. 在bilibili.com > Cookie 下找到SESSDATA字段
	![获取cookie](/images/getCookies3.jpg "获取cookie")
	![获取cookie](/images/getCookies4.jpg "获取cookie")
	
	***将SESSDATA泄露给他人可能会导致账号被盗!!***

### 3. 确定下载范围
​		在出现漫画详情后, 输入下载范围

### 4. 静待下载完毕
​		接下来程序会自动开始下载, 下载速度取决于网络质量和地理位置。

## 改进项目
​		项目欢迎各位开发者提交contribution! 

​		如果有帮助到您，可以点个Star!

​		技术交流可以加我QQ 3525904273 (学生党 可能不能随时回复)

## 问题排除

1. 提示各种内容损坏：
   检查网络状态，检查是否能够访问B漫
   检查运行环境的`python, requests, hashlib`版本

2. 没有提示内容损坏，但是下载下来的图片出现损坏

   删除`/data`文件夹下相应文件夹并重新下载。

_如仍有故障，可以请联系我 (QQ: 3525904273) 解决。_
