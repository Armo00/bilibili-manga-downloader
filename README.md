# bilibili-manga-downloader
下载哔哩哔哩漫画的爬虫， 支持范围下载， 逐话导出PDF，自动合并PDF

__GUI版本已经开始制作!__

## 项目特点
1. 支持多线程下载
2. 可自定义下载范围
3. 可以导出每一话的PDF文件
4. 自动合并PDF 并生成Kindle可读的标签
## 运行环境
Python 3.x
在CMD或BASH中执行这行代码安装运行库:```pip3 install -r  requirements.txt```

## 使用方法
在CMD或BASH中执行这行代码
```
python3 main.py
```
执行后按照提示输入参数

### 	1. 获取漫画ID(comicID):

​		进入漫画详情页(如图)
​		![漫画详情](/images/info.jpg "漫画详情")(https://manga.bilibili.com/detail/mc25493?from=manga_search)
​		此时的链接 manga.bilibili.com/detail/mc***25493***?from=manga_search 中的/mc***xxxxx***就是漫画ID

### 2. 付费漫画下载 SESSDATA获取
​		如果要下载付费漫画, 则需要登录自己的账号, 并输入SESSDATA(免费漫画无需)

​		请在浏览器登录BiliBili漫画后, 获取cookies中的"SESSDATA"

1. 点击链接框前小锁符号
	![获取cookie](/images/getCookies1.jpg "获取cookie")
2. 点击Cookie字段
	![获取cookie](/images/getCookies2.jpg "获取cookie")
3. 在bilibili.com > Cookie 下找到SESSDATA字段
	![获取cookie](/images/getCookies3.jpg "获取cookie")
	![获取cookie](/images/getCookies4.jpg "获取cookie")
	
	***切记 将SESSDATA泄露给他人会导致账号被盗!!***

### 3. 确定下载范围
​		在出现漫画详情后, 输入下载范围

### 4. 静待下载完毕
​		恭喜您! 接下来程序会自动开始下载, 下载速度取决于下载量

## 改进项目
​		项目欢迎各位开发者提交contribution! 喜欢请点个Star!
​		技术交流可以加我QQ 3525904273 (学生党 可能不能随时回复)