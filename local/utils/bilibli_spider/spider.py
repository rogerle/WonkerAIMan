from urllib import parse
import json
import requests
from collections import namedtuple
from lxml import etree
import os
import re
import uuid
from collections.abc import Iterable


class serialize:
    def __init__(self, d):
        self.__dict__ = d


def re_tag(text):
    # pattern = re.compile(r'【[^>]+>]',re.S)
    # result = pattern.sub('',text)
    # print(result)
    # return result
    res = etree.HTML(text=text)
    print(res.xpath('string(.)'))
    return res.xpath('string(.)')


def get_data(url, headers):
    header = headers
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        return response


def flatten(items, ignore_types=(str, bytes)):
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, ignore_types):
            yield from flatten(x)
        else:
            yield x


class BilibliSpider:

    # 初始化搜索关键字，
    def __init__(self, search_key):
        self.search_key = search_key
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54'}
        self.dir = 'Bilibi'

    # 初始化interface_search接口，返回json对象，能够获取结果的bv页面详情
    def get_interface_search(self, page, page_size):

        t = []
        keyword = parse.quote(self.search_key)
        url = f'https://api.bilibili.com/x/web-interface/search/type?page={page}&page_size={page_size}&keyword={keyword}&search_type=video'

        response = get_data(url, self.headers)
        res = response.text
        # print(res)
        p = json.loads(res, object_hook=serialize)
        for i in p.data.result:
            d = {}
            d['author'] = i.author
            d['arcurl'] = i.arcurl
            d['aid'] = i.aid
            d['bvid'] = i.bvid
            d['title'] = re_tag(i.title)
            d['description'] = re_tag(i.description)
            t.append(d)
        return t

    # 单页面获取dash的url
    def get_dash_url(self, avurl):
        res = get_data(avurl, self.headers)
        res = res.text
        html = etree.HTML(res)
        res = html.xpath('/html/head/script[4]/text()')[0].split('=', 1)[-1]
        res_json= json.loads(res,object_hook=serialize)
        video = res_json.data.dash.video[0]
        audio = res_json.data.dash.audio[0]
        video_baseUrl = video.baseUrl
        video_backupUrl = video.backupUrl
        audio_baseUrl = audio.baseUrl
        audio_backupUrl = audio.backupUrl
        return {'video_baseUrl':video_baseUrl,'video_backupUrl':video_backupUrl,'audio_baseUrl':audio_baseUrl,'audio_backupUrl':audio_backupUrl}


    # 下载单个video
    def save_dash(self, url, avUrl):
        header = self.headers
        header.update({'Referer': avUrl})
        res = get_data(url=url, headers=header)
        print(url, avUrl)
        filename = "{}.mp4".format(uuid.uuid4().hex)
        with open(filename, 'wb') as f:
            f.write(res.content)
        return filename

    # 创建目录
    def is_mkdir(self, title):
        path = os.path.join(self.dir, title)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    # 合并video
    def merge_video(self, input_audio, input_video, output_video):
        import subprocess
        cmd = f'ffmpeg -i {input_audio} -i {input_video} -acodec copy -vcodec copy {output_video} '
        subprocess.call(cmd, shell=True)
        return True

    # 保存弹幕
    def save_tantantan(self):
        pass

    # 保存封面
    def save_page(self):
        pass

    # 下载bv
    def save_bv(self, url,title=None):

        if title == None:
            title = url.split('/')[-1]
        dict_t = self.get_dash_url(url)
        video_baseUrl = dict_t['video_baseUrl']
        audio_baseUrl = dict_t['audio_baseUrl']
        video_name = self.save_dash(url=video_baseUrl,avUrl=url)
        audio_name = self.save_dash(url=audio_baseUrl,avUrl=url)
        outname1 =  "{}-{}.mp4".format(title,0)
        self.merge_video(video_name,audio_name,outname1)
        os.remove(video_name)
        os.remove(audio_name)
        count = 1
        for i in zip(dict_t['video_backupUrl'],dict_t['audio_backupUrl']):
            outname = "{}-{}.mp4".format(title,count)
            video = self.save_dash(url=i[0], avUrl=url)
            audio = self.save_dash(url=i[1], avUrl=url)
            self.merge_video(video, audio, outname)
            os.remove(video)
            os.remove(audio)
            count += 1

    # 下载多个bv
    def save_bv_many(self):
        pass

    # by_key_save_video
    def save_by_key(self):
        pass


if __name__ == '__main__':
    B = BilibliSpider('星露谷')
    test = 'https://www.bilibili.com/video/BV1La411N7qS'
    # res = B.get_interface_search(2, 42)
    # print(B.result)
    # B.get_dash_url(test)
    # print(B.urls_video)
    B.save_bv(test)