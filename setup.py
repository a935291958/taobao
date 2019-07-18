# -*- coding: UTF-8 -*-
# add : ‎2019‎年‎7‎月‎15‎日
# update : 2019年7月18日
# author : 蔡锦龙
# email : bearshop.cc@qq.com

import urllib.request as request, sys, json, time, html, configparser, pymysql
from common import *
from urllib import parse

# --*-- 配置信息 S --*--

# 组装配置信息ini文件路径
curpath = os.path.dirname(os.path.realpath(__file__))
cfgpath = os.path.join(curpath, "config/config.ini")  # 读取到本机的配置文件

# 调用读取配置模块中的类
config = configparser.ConfigParser()
config.read(cfgpath, encoding="utf-8")

keyword = open('config/keyword.txt').read()  # 关键字列表
pageCount = int(config.get('user', 'pageCount'))  # 采集前几页
delOldData = int(config.get('user', 'delOldData'))  # 是否删除旧文件
cookie = str(open('config/cookie.txt', 'rb').read())  # cookie
sleepTimeStart = int(config.get('user', 'sleepTimeStart'))  # 采集完1页休眠时间
sleepTimeEnd = int(config.get('user', 'sleepTimeEnd'))  # 采集完1页休眠时间

# --*-- 配置信息 E --*--

# 删除旧文件目录下面的所有文件
if int(delOldData) > 0:
    remove_dir('result')

# 分割关键字列表
kw = keyword.split('\n')

# 源文件关键字长度
kwLen = len(kw)
msg('源文件关键字长度：%d 个' % kwLen, 1)
# 如果关键字长度小于1，就退出
if kwLen < 1:
    msg('源文件关键字长度小于1，程序退出', 2)
    sys.exit(0)

for ki in range(kwLen):

    # 删除前后空格
    kw[ki].strip()

    # 删除空的关键字列表元素
    if not kw[ki]:
        del kw[ki]
    pass

# 去除空行后的关键字长度
kwLenNew = len(kw)
msg('有效关键字长度：%d 个' % kwLenNew, 1)
# 如果关键字长度小于1，就退出
if kwLenNew < 1:
    msg('有效关键字长度小于1，程序退出', 2)
    sys.exit(0)

sTime = int(round(time.time() * 1000))
msg("开始执行：%s" % sTime, 1)

# 请求头
headers = {
    'authority': 's.taobao.com'
    , 'method': 'GET'
    ,
    'path': '/search?q=%E7%9F%AD%E8%A3%99&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190710&ie=utf8&sort=sale-desc'
    , 'scheme': 'https'
    ,
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
    # ,'accept-encoding': 'gzip, deflate, br'
    , 'accept-language': 'zh-CN,zh;q=0.9'
    , 'cache-control': 'no-cache'
    ,
    'cookie': cookie
    , 'pragma': 'no-cache'
    ,
    'referer': 'https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=%E6%B7%98%E5%AE%9D%E6%95%B0%E6%8D%AE%E7%88%AC%E5%8F%96&suggest=0_3&_input_charset=utf-8&wq=%E6%B7%98%E5%AE%9D%E6%95%B0%E6%8D%AE&suggest_query=%E6%B7%98%E5%AE%9D%E6%95%B0%E6%8D%AE&source=suggest'
    , 'upgrade-insecure-requests': 1
    ,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'

}


# 替换符号
def symbol(string):
    return string.replace(',', '，')


def getOne(url, page, key):
    # 休眠，以防检测
    sleepTime = random.randint(sleepTimeStart, sleepTimeEnd)  # 随机生成一个时间
    msg('当前关键字：【 %s 】' % key, 1)
    msg('休眠 %d 秒' % sleepTime, 1)
    time.sleep(sleepTime)

    # 追加分页参数 S
    if page < 2:
        url = url
    else:
        # 分页的url
        pageUrl = '&s=' + str(page * 44)
        # //获取分页的值
        pageSearch = re.search(r'&s=([0-9]+)$', url)
        if not pageSearch:
            url = url + pageUrl
        else:
            url = url.replace(pageSearch.group(0), pageUrl)
    # 追加分页参数 E
    msg('进行第 %d 页采集，链接：%s ' % (page, url), 1)
    req = request.Request(url=url, headers=headers)

    # 请求访问
    res = request.urlopen(req)

    # 读取返回的内容
    htmlBytes = res.read()

    # 转成string
    htmlStr = str(htmlBytes, encoding="UTF-8")

    # 判断有木有访问成功
    if htmlStr.find('g_page_config') < 0:
        msg('访问未成功，程序退出', 3)
        sys.exit(0)
        pass

    # 截取返回结果
    g_page_config = re.search(r'g_page_config = (.*}})', htmlStr, re.M | re.I)

    # 判断有木有成功截取到数据
    if not g_page_config or not g_page_config.group(1):
        msg('未能匹配到数据', 3)
        sys.exit(0)
        pass

    # 转成JSON
    lists = json.loads(g_page_config.group(1))

    # 商品列表
    shoplist = lists['mods']['itemlist']['data']['auctions']

    # 页数
    totalPage = lists['mods']['pager']['data']['totalPage']

    # 搜索总数
    totalCount = lists['mods']['pager']['data']['totalCount']

    # 分页大小
    pageSize = lists['mods']['pager']['data']['pageSize']

    json_dicts = json.dumps(shoplist)

    # print(shoplist[1])
    # print(json_dicts)
    msg(('当前页面商品总数：%s' % pageSize), 1)
    msg(('总页数： %s' % totalPage), 1)
    msg(('剩余采集商品总数：%s' % totalCount), 1)

    # 遍历商品列表
    notSum = 0
    # 打开存放文件
    dataFileName = 'result/' + key + '.csv'

    # 如果不存在，就先写入标题
    if not isFile(dataFileName):
        dataFile = open(dataFileName, 'a+', encoding='gbk')

        dataTitle = '商品链接,详情链接,店铺名称,地址,大图,原标题,高亮关键字标题,付款人数,显示的价格,添加时间\n'
        dataFile.write(dataTitle)
    else:
        dataFile = open(dataFileName, 'a+', encoding='gbk')
        pass

    for i in shoplist:
        if 'p4p' in i:
            notSum = notSum + 1
            continue
        # 替换英文逗号
        row = symbol(html.unescape(i['comment_url'])) \
              + ',' + symbol(i['detail_url']) \
              + ',' + symbol(i['nick']) \
              + ',' + symbol(i['item_loc']) \
              + ',' + symbol(i['pic_url']) \
              + ',' + symbol(i['raw_title']) \
              + ',' + symbol(i['title']) \
              + ',' + symbol(i['view_sales']) \
              + ',' + symbol(i['view_price']) \
              + ',' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n'

        dataFile.write(row)
        # for end
        pass
    # 写入完成，关闭文件
    dataFile.close()
    # 继续下一页
    if page < totalPage and page <= pageCount:
        page = page + 1
        getOne(url, page, key)
    else:

        msg('采集列表已完成', 1)

    # resFile = open('res.html', 'a')
    # resFile.write('\n<script>a = ' + json_dicts + ';console.log(a);</script>\n')
    # resFile.close()

    pass


def main():
    # 判断存放结果的目录存不存在
    if not isDir('result'):
        os.mkdir('result')
    # 第一次请求的url
    for ki in kw:
        # 关键字url编码
        keyword = parse.quote(ki)
        url = 'https://s.taobao.com/search?q=' + keyword + '&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190715&ie=utf8&sort=sale-desc'
        getOne(url, 1, ki)
    pass


if __name__ == '__main__':
    main()

eTime = int(round(time.time() * 1000))
msg("结束执行：%s" % eTime, 1)
msg("共耗时：%s 秒" % int((eTime - sTime) / 1000), 1)
