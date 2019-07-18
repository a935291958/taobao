# -*- coding: UTF-8 -*-

import urllib.request as request, sys, json, pymysql, time, html, configparser
from common import *
from urllib import parse

# --*-- 配置信息 S --*--

# 组装配置信息ini文件路径
curpath = os.path.dirname(os.path.realpath(__file__))
cfgpath = os.path.join(curpath, "config/config.ini")  # 读取到本机的配置文件

# 调用读取配置模块中的类
config = configparser.ConfigParser()
config.read(cfgpath, encoding="utf-8")

keyword = config.get('user', 'keyword')  # 搜素的关键字
pageCount = int(config.get('user', 'pageCount'))  # 采集前几页
cookie = str(open('config/cookie.txt', 'rb').read())  # cookie
sleepTimeStart = int(config.get('user', 'sleepTimeStart'))  # 采集完1页休眠时间
sleepTimeEnd = int(config.get('user', 'sleepTimeEnd'))  # 采集完1页休眠时间


mysqlUser = config.get('mysql', 'user')  # 数据库账号
mysqlPass = config.get('mysql', 'pass')  # 数据库密码
mysqlTb = config.get('mysql', 'tb')  # 数据库库名
mysqlChar = config.get('mysql', 'char')  # 数据库字符集

# --*-- 配置信息 E --*--


sTime = int(round(time.time() * 1000))
msg("开始执行：%s" % sTime, 1)

# 连接MySQL
mysqlCon = pymysql.connect(user=mysqlUser, password=mysqlPass, database=mysqlTb, charset=mysqlChar)
mysql = mysqlCon.cursor()
# 清空商品列表
delShopRes = mysql.execute('truncate table `tb_shop`')
msg('清空数据库商品列表', 1)

# 查询表结构SQL --- 商品列表
query = 'desc tb_shop'
# 表字段列表 --- 商品列表
structure = []
res = mysql.execute(query)
for i in mysql:
    structure.append(i[0])

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

# 第一次请求的url
# 关键字url编码
keyword = parse.quote(keyword)
url = 'https://s.taobao.com/search?q=' + keyword + '&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190715&ie=utf8&sort=sale-desc'


# 生成增加的SQL
# table 表
# structure 字段列表
def sqlInstall(insData, table='tb_shop', structure=structure):
    insSql = 'INSERT  INTO ' + table + '( '
    filed = ''
    value = ''
    for i in insData:
        if i in structure:
            filed += '`' + i + '`,'
            value += '"' + html.escape(insData[i]) + '",'
    insSql = insSql + filed[0:-1] + ' ) value( ' + value[0:-1] + ' )'
    msg('SQL: ' + insSql, 5)
    # 插入数据
    insRes = mysql.execute(insSql)
    if insRes < 0:
        msg('执行SQL失败: %s' % insSql, 2)
    pass


def main(url, page):
    # 休眠，以防检测
    sleepTime = random.randint(sleepTimeStart, sleepTimeEnd)  # 随机生成一个时间
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
    for i in shoplist:
        if 'p4p' in i:
            notSum = notSum + 1
            continue
        # print(i)
        # 取出所需的数据
        insData = {}
        insData['comment_url'] = html.unescape(i['comment_url'])
        insData['detail_url'] = i['detail_url']
        insData['nick'] = i['nick']
        insData['pic_url'] = i['pic_url']
        insData['raw_title'] = i['raw_title']
        insData['title'] = i['title']
        insData['view_sales'] = i['view_sales']
        insData['view_price'] = i['view_price']
        insData['item_loc'] = i['item_loc']
        insData['addtime'] = time.strftime("%Y-%m-%d %H:%M:%S")

        # 插入数据
        sqlInstall(insData)
        # for end
        pass

    # 继续下一页
    if page < totalPage and page <= pageCount:
        page = page + 1
        main(url, page)
    else:
        msg('采集列表已完成', 1)

    # resFile = open('res.html', 'a')
    # resFile.write('\n<script>a = ' + json_dicts + ';console.log(a);</script>\n')
    # resFile.close()

    pass


if __name__ == '__main__':
    main(url,1)

# 关闭MySQL
mysql.close()
eTime = int(round(time.time() * 1000))
msg("结束执行：%s" % eTime, 1)
msg("共耗时：%s 秒" % int((eTime - sTime) / 1000), 1)
