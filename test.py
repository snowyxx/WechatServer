#!C:\Python27\python.exe
# coding:utf-8
import web
import time
import hashlib
import urllib2
import re
import random
import xml.dom.minidom
from conf import wxLogger
from conf import products

urls = (
    "/", "hello",
    "/getnickname", "getnickname"
)

web.config.debug = True
app = web.application(urls, globals())
render = web.template.render('templates/')

class getnickname:
    '''demo class to fetch user name with Oauth2 code. 
    ***JUST FOR DEMO ***
    http://mp.weixin.qq.com/wiki/17/c0f37d5704f0b64713d5d2c37b468d75.html
    http://qydev.weixin.qq.com/wiki/index.php?title=%E9%A6%96%E9%A1%B5
    '''
    def GET(self):
        try:
            data = web.input()
            wxLogger.info(data)
            code = data.code
            atype = data.atype
            if atype == 'sub':
                Oauthurl = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={0}&secret={1}&code={2}&grant_type=authorization_code'.format('your app id', 'your secret', code)
                response = urllib2.urlopen(Oauthurl).read().decode('utf-8')
                wxLogger.info(response)
                resDir = json.loads(response)
                openid = resDir['openid']
                access_token = resDir['access_token']
                userInfoUrl = 'https://api.weixin.qq.com/sns/userinfo?access_token={0}&openid={1}&lang=zh_CN'.format(access_token, openid)
                response = urllib2.urlopen(userInfoUrl).read().decode('utf-8')
                wxLogger.info(response)
                resDir = json.loads(response)
                nickname = resDir['nickname']
            elif atype == 'ent':
                #get api access_token   http://qydev.weixin.qq.com/wiki/index.php?title=%E4%B8%BB%E5%8A%A8%E8%B0%83%E7%94%A8
                url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={0}&corpsecret={1}".format('your app id', 'your secret')
                response = urllib2.urlopen(url).read().decode('utf-8')
                resDir = json.loads(response)
                access_token = resDir['access_token']
                
                #get user id   http://qydev.weixin.qq.com/wiki/index.php?title=OAuth%E9%AA%8C%E8%AF%81%E6%8E%A5%E5%8F%A3
                url = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token={0}&code={1}".format(access_token, code)
                response = urllib2.urlopen(url).read().decode('utf-8')
                resDir = json.loads(response)
                userid = resDir['UserId']
                
                #get user name http://qydev.weixin.qq.com/wiki/index.php?title=%E7%AE%A1%E7%90%86%E6%88%90%E5%91%98#.E8.8E.B7.E5.8F.96.E6.88.90.E5.91.98
                url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={0}&userid={1}'.format(access_token, userid)
                response = urllib2.urlopen(url).read().decode('utf-8')
                resDir = json.loads(response)
                username = resDir['name']
                nickname = username
            else:
                nickname = 'Unknown user from WeChat'
            return nickname
        except Exception, e:
            return 'Unknown user from WeChat'

class hello:

    def GET(self):
        try:
            data = web.input()
            wxLogger.info(data)
            signature = data.signature
            timestamp = data.timestamp
            nonce = data.nonce
            echostr = data.echostr
            token = "xxxxxx"
            list = [token, timestamp, nonce]
            list.sort()
            sha1 = hashlib.sha1()
            map(sha1.update, list)
            hashcode = sha1.hexdigest()
            if hashcode == signature:
                return echostr
        except Exception, e:
            return ''
        data = web.input()
        wxLogger.info(data)
        signature = data.signature
        timestamp = data.timestamp
        nonce = data.nonce
        echostr = data.echostr
        token = "xxxxxx"
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        map(sha1.update, list)
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return echostr

    def POST(self):
        str_xml = web.data()
        try:
            domTree = xml.dom.minidom.parseString(str_xml)
            collection = domTree.documentElement
            ToUserName = collection.getElementsByTagName('ToUserName')[0].childNodes[0].data
            FromUserName = collection.getElementsByTagName('FromUserName')[0].childNodes[0].data
            MsgType = collection.getElementsByTagName('MsgType')[0].childNodes[0].data
        except Exception, e:
            return ''
        
        Content = ''
        Event = ''
        try:
            Content = collection.getElementsByTagName('Content')[0].childNodes[0].data
        except IndexError:
            pass
        try:
            Event = collection.getElementsByTagName('Event')[0].childNodes[0].data
        except IndexError:
            pass
        if Event:
            if Event == 'subscribe':
                answer = '欢迎关注！\n输入“使用”和我们交流吧。'
                return render.wx(ToUserName, FromUserName, int(time.time()), answer)
            else:
                wxLogger.info('[!]The message/event we did not handle\n'+str_xml)
                return
        answer = ''
        productnames = [p['name'].lower() for p in products] + [p['shortname'].lower() for p in products]
        if Content[0:2] == u'产品':
            pname = Content[2:].strip().lower()
            if not pname:
                pname = "me"
            answer = self.getProductInfo(pname)
            return render.wx(ToUserName, FromUserName, int(time.time()), answer)
        elif Content.lower() in productnames:
            answer = self.getProductInfo(Content.lower())
            return render.wx(ToUserName, FromUserName, int(time.time()), answer)
        elif Content[0:2] == u'归档':
            pname = Content[2:].strip().lower()
            if not pname:
                pname = "me"
            for product in products:
                if pname == product['name'].lower() or pname == product['shortname'].lower():
                    answer = "%s" % (product['archives'])
                    break
            if not answer:
                plist = [p['name']+'('+p['shortname']+')' for p in products]
                answer = '没有该产品的信息。\n当前提供以下产品信息(不区分大小写)：\n' + '\n'.join(plist)
            wxLogger.info('[!] User requested a unexisting product: %s' % pname)
            return render.wx(ToUserName, FromUserName, int(time.time()), answer)
        elif re.match('^goodluck\*?(\d*)$', Content):
            count = re.match('^goodluck\*?(\d*)$', Content).group(1)
            count_int = int(count) if count else 1
            if count_int > 10:
                count_int = 10
                answer += '太多了，先来10个吧:)'

            if count_int > 1:
                for x in range(count_int):
                    answer += '\n' + ' '.join(map(str, sorted(random.sample(range(1, 34), 6)))) + ' - ' + str(random.randint(1, 16))
            else:
                answer = ' '.join(map(str, sorted(random.sample(range(1, 34), 6)))) + ' - ' + str(random.randint(1, 16))
            return render.wx(ToUserName, FromUserName, int(time.time()), answer.strip())
        elif Content[0:2] == u'使用':
            usage = "*使用方法：\n- 输入“产品+产品名”，或直接输入“产品名”，获取产品信息\n- 输入“归档+产品名”，获取产品归档地址\n- 输入“下载+产品名”，获取产品下载地址"
            return render.wx(ToUserName, FromUserName, int(time.time()), usage)
        else:
            # wxLogger.info('[!]The message/event we did not handle\n'+str_xml)
            url = 'http://www.qiushibaike.com/hot/'
            headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
            request = urllib2.Request(url, headers=headers)
            responese = urllib2.urlopen(request)
            pagecode = responese.read()
            pattern = re.compile(r'(?is)<div class="content">(.*?)</div>')
            items = re.findall(pattern, pagecode)
            random.shuffle(items)
            return render.wx(ToUserName, FromUserName, int(time.time()), items[0].strip().replace('<br/>', '')+'\n--来自糗事百科\n* 输入“使用”和我们交流吧。')

    def getProductInfo(self, productname):
        answer = ''
        for product in products:
            pdes = product['des']
            if productname == product['name'].lower() or productname == product['shortname'].lower():
                iszh = '提供中文界面' if product['ifzh_CN'] else '不提供中文界面'
                build = '和英文版同步' if product[
                    'lastBuild'] == '' else product['lastBuild']
                answer = "产品名称：%s\n%s\n最后中文版本：%s\n网站：%s\n简介：%s" % (
                    product['name'], iszh, build, product['webSite'], pdes)
                break
        if not answer or productname == 'me':
            if not answer:   # :(
                wxLogger.info('[!] User requested an unexisting product: %s' % productname)
            plist = [p['name']+'或'+p['shortname'] for p in products]
            answer += '没有该产品的信息。\n当前提供以下产品信息(不区分大小写)：\n' + '\n'.join(plist)
        return answer

if __name__ == '__main__':
    app.run()