import os
import shutil
from rich import print
from rich.table import Table
from rich.console import Console
from rich.progress import Progress, track
import requests
import datetime
import time
from retry import retry
import threading
import json
import img2pdf
from PyPDF4 import PdfFileMerger, PdfFileReader
import hashlib

console = Console()


def _time():
    t = datetime.datetime.fromtimestamp(time.time())
    timeStr = t.strftime("[ %Y.%m.%d %H:%M:%S ]")
    return "[rgb(102, 102, 153)]%s[/]" % timeStr


def info(msg):
    timeStr = _time()
    logStr = "%s [b]|[rgb(51, 204, 204)]INFO[/]|[/b] %s" % (timeStr, msg)
    print(logStr)


def error(msg):
    timeStr = _time()
    logStr = "%s [b]|[rgb(204, 0, 0)]ERROR[/]|[/b] %s" % (timeStr, msg)
    print(logStr)


def isInt(a):
    try:
        int(a)
        return True
    except:
        return False


def ceil(num):
    if isinstance(num, (float,)):
        return int(num) + 1
    else:
        return num


def splitThreads(data, num):
    for i in range(ceil(len(data) / num)):
        _from = i * num

        _to = (i + 1) * num
        if _to >= len(data):
            _to = len(data)
        yield data[_from:_to]


def _sorted(data):
    for i in range(len(data) + 1):
        for j in range(len(data)):
            if j > 0:
                a = data[j - 1].split('.')[0]
                b = data[j].split(".")[0]
                fa, sa = a.split('_')
                fb, sb = b.split('_')
                if int(fa) > int(fb):
                    data[j - 1], data[j] = data[j], data[j - 1]
                elif int(fa) == int(fb):
                    if int(sa) > int(sb):
                        data[j - 1], data[j] = data[j], data[j - 1]

    return data


# 测试

class Episode:
    """
        一集
    """

    def __init__(self, jsonData, sessData, comicID):
        self.id = jsonData['id']
        self.available = not jsonData['is_locked']
        self.ord = jsonData['ord']  # 真正的顺序..
        # 使用short_title作为显示/标注用的标题
        self.title = jsonData['short_title']
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.56',
            'origin': 'https://manga.bilibili.com',
            'referer': f'https://manga.bilibili.com/detail/mc{comicID}/{self.id}?from=manga_homepage',
            'cookie': f'SESSDATA={sessData}'

        }
        self.rootPath = './data/' + str(comicID)

    def getAvailable(self):
        return self.available

    @retry(delay=1)
    def downloadImg(self, token, url, index):
        url = url + "?token=" + token
        file = requests.get(url)
        
        if file.headers['Etag'] != hashlib.md5(file.content).hexdigest():
            error(f"下载内容校验和不正确! {file.headers['Etag']} ≠ {hashlib.md5(file.content).hexdigest()}")
            # raise Exception

        with open(os.path.join(self.rootPath, f"{self.ord}_{index}.jpg"), 'wb') as f:
            f.write(file.content)

        # 返回头的ETag正好是文件的md5校验和
        # 旧的校验方式: 文件大小
        # if size != int(file.headers['content-length']):
        #    error(f"下载内容大小不符合预期! 预期大小: {file.headers['content-length']} 实际大小: {size} 1s后重试!")
        #    raise Exception

        return os.path.join(self.rootPath, f"{self.ord}_{index}.jpg")

    def download(self):
        url = 'https://manga.bilibili.com/twirp/comic.v1.Comic/GetImageIndex?device=pc&platform=web'
        payloads = {
            'ep_id': self.id
        }
        if os.path.exists(self.rootPath + f'/{self.ord}.pdf'):
            # 相同文件名已经存在 跳过下载
            return
        rep = requests.post(url, data=payloads, headers=self.headers)
        if rep.ok:
            data = rep.json()
            images = data['data']['images']
            paths = []
            for img in images:
                paths.append(img['path'])
            payloads = {
                "urls": json.dumps(paths).decode()
            }
            url = "https://manga.bilibili.com/twirp/comic.v1.Comic/ImageToken?device=pc&platform=web"

            @retry(delay=1)
            def _():
                return requests.post(url, data=payloads, headers=self.headers)

            imgs = []
            rep = _()
            if rep.ok:
                i = 1
                for img in rep.json()['data']:
                    imgs.append(self.downloadImg(img['token'], img['url'], i))
                    i += 1

                    # progress.update(tid, advance=1, total=len(images), description=f'正在下载第{self.ord}话 "{self.title}"')
                with open(self.rootPath + f'/{self.ord}.pdf', 'wb') as f:
                    f.write(img2pdf.convert(imgs))

                @retry()
                def _():
                    for img in imgs:
                        os.remove(img)

                _()


class Comic:
    """
        一个漫画
    """

    def __init__(self, comicID: int, sessdata: str) -> None:
        # 初始化
        if len(sessdata) == 0:
            self.sessdata = False
        else:
            self.sessdata = sessdata
        info(f'初始化漫画 ID {comicID}')
        self.id = comicID
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.56',
            'origin': 'https://manga.bilibili.com',
            'referer': f'https://manga.bilibili.com/detail/mc{comicID}?from=manga_homepage',
        }
        if self.sessdata:
            self.headers.update({'cookie': f'SESSDATA={self.sessdata}'})

        self.detailUrl = 'https://manga.bilibili.com/twirp/comic.v1.Comic/ComicDetail?device=pc&platform=web'
        self.threads = 30

        # 属性
        self.title = 'Nope'
        self.authorName = []
        self.styles = []
        self.evaluate = 'Nope'
        self.total = 0
        self.episodes = []
        self.success = False

    def fetch(self):
        @retry()
        def mkdir():
            os.mkdir(f'./data/{self.id}')
        if not os.path.exists('./data'):
            os.mkdir('./data')
        if os.path.exists(f'./data/{self.id}'):
            if os.path.isdir(f'./data/{self.id}'):
                # shutil.rmtree(f'./data/{self.id}')
                info('存在历史下载 将避免下载相同文件!')
            else:
                os.remove(f'./data/{self.id}')
                mkdir()
        else:
            mkdir()


        payload = {"comic_id": self.id}
        with console.status('正在访问BiliBili Manga'):
            rep = requests.post(self.detailUrl, data=payload, headers=self.headers)
        if rep.ok:
            info('漫画信息GET XD')
            info('开始解析信息...')
            # try:
            data = rep.json()
            self.analyzeData(data)
            # 开始爬取
            with Progress() as progress:
                epiTask = progress.add_task(f'正在下载 <{self.title}>', total=len(self.episodes))
                # progressIDS = []
                # for t in range(self.threads):
                #     progressIDS.append(progress.add_task(f'thread {t}'))
                for epis in splitThreads(self.episodes, self.threads):
                    i = 0
                    # ids = progressIDS[:len(epis)]
                    threads = []
                    for epi in epis:
                        t = threading.Thread(target=epi.download)
                        t.start()
                        threads.append(t)

                    for t in threads:
                        t.join()
                        progress.update(epiTask, advance=1)
                    # time.sleep(0.5)
            if os.path.exists(f'./{self.id}.pdf'):
                os.remove(f'./{self.id}.pdf')
            merger = PdfFileMerger()
            for pdf in track(self.episodes, description='正在合并PDF...'):
                path = os.path.join('.', 'data', str(self.id), f'{pdf.ord}.pdf')
                if os.path.exists(path):
                    merger.append(PdfFileReader(path), bookmark=pdf.title)
            merger.write(f'./{self.id}.pdf')

            info('任务完成!')
            # shutil.rmtree(f'./data/{self.id}')
            # images = []
            # for img in _sorted(os.listdir('./data/' + str(self.id))):
            #     images.append(os.path.join('./data/' + str(self.id), img))
            # with open(f'./{self.id}.pdf', 'wb') as f:
            #     f.write(img2pdf.convert(images))
            # info('转换成功!')
            # except:
            #     error('情报有误! ')
            #     error(f'详细信息: {rep.text}')

        else:
            error('请求错误 / 网络错误!')
            error(f'详细信息: {rep.status_code}')
            error("请检查输入信息是否正确!")

    def analyzeData(self, data):
        if data['code'] != 0:
            error(f'漫画信息有误! 请仔细检查! (提示信息{data["msg"]})')
            return False

        self.title = data['data']['title']
        self.authorName = data['data']['author_name']
        self.styles = data['data']['styles']
        self.evaluate = data['data']['evaluate']
        self.total = data['data']['total']
        t = Table(title='漫画作品详情')
        t.add_column('[green bold]作品标题[/green bold]')
        t.add_column('[green bold]作者[/green bold]')
        t.add_column('[green bold]标签[/green bold]')
        t.add_column('[green bold]概要[/green bold]')
        t.add_column('[green bold]总章节[/green bold]')
        t.add_row(self.title, ', '.join(self.authorName),
                  ''.join(self.styles), self.evaluate, str(self.total))
        self.episodes = []
        self.ordTitle = {}
        console.print(t)
        _from = requireNumber('开始章节(ord): ', False)
        if _from is None:
            # 不输入则不限制
            _from = 0
        _to = requireNumber('结束章节(ord): ', False)
        if _to is None:
            # 不输入则不限制
            _to = 999999999
        # 允许小于等于才能够下载单章以及输入两个0下载全部
        assert _from <= _to

        # with open('debug.json', 'wb') as f:
        #     f.write(json.dumps(data))
        with console.status('正在解析详细章节...'):
            epList = data['data']['ep_list']
            epList.reverse()
            for episode in epList:
                # BiliBili漫画索引号是反着的
                epi = Episode(episode, self.sessdata, self.id)
                if epi.getAvailable():
                    # 直接比较即可，之前的方式会导致预期之外的添加
                    if _from <= epi.ord <= _to:
                        self.episodes.append(epi)
                        self.ordTitle[epi.ord] = epi.title
                    if (not bool(_from)) and (not bool(_to)):
                        self.episodes.append(epi)
                        self.ordTitle[epi.ord] = epi.title

        info(f'分析结束 将爬取章节数: {len(self.episodes)}/{self.total} 准备开始爬取!')
        return True


def requireInt(msg, notNull):
    while 1:
        userInput = input(msg)
        try:
            if len(userInput) == 0 and (not notNull):
                return None
            return int(userInput)
        except ValueError:
            error('请输入数字...')

def requireNumber(msg, notNull):
    while 1:
        userInput = input(msg)
        try:
            if len(userInput) == 0 and (not notNull):
                return None
            return float(userInput)
        except ValueError:
            error('请输入数字...')

if __name__ == '__main__':
    comicID = requireInt('请输入漫画ID:', True)
    userInput = input('请输入SESSDATA (免费漫画请直接按下enter):')
    sessdata = userInput
    c = Comic(comicID, sessdata)
    c.fetch()
    input("按Enter键退出...")