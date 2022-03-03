import requests
import warnings
import re
import time
import ddddocr

warnings.filterwarnings('ignore')

class discuzLogin:

    #代理
    proxies = {
        'http': 'http://127.0.0.1:1080',
        'https': 'https://127.0.0.1:1080'
    }

    #请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    #初始化对象
    def __init__(self, hostname, username, password, questionId='0', answer=None, poxies=None):
        # 创建session
        self.session = requests.session()

        # 传登录参数
        self.hostname = hostname    #登录网址
        self.username = username    #用户名
        self.password = password    #密码
        self.questionId = questionId    #登录问题
        self.answer = answer    #登录问题答案
        self.proxies = poxies   #代理

    @classmethod
    #登录方法入口
    def userLogin(cls, hostname, username, password, questionId='0', answer=None, proxies=None):

        #创建登录对象并传入登录参数
        user = discuzLogin(hostname, username, password, questionId, answer, proxies)

        #登录
        t = user.login(hostname)

        #若登录失败则重新尝试登录
        #由于ddddOCR识别验证码正确率较低，故需要重复模拟登录直到登录成功
        while t == False:
            t = user.login(hostname)

    #获取loginhash和formhash
    def formHash(self):

        #获取登录页面html文本
        rst = self.session.get(f'https://{self.hostname}/member.php?mod=logging&action=login', verify=False,
                               headers=self.headers).text

        #使用正则匹配获取loginhash和formhash
        loginhash = re.search(r'<div id="main_messaqge_(.+?)">', rst).group(1)
        formhash = re.search(r'<input type="hidden" name="formhash" value="(.+?)" />', rst).group(1)

        return loginhash, formhash

    def login(self, hostname):

        #获取loginhash和formhash
        loginhash, formhash = self.formHash()

        #获取验证码图片
        verify = self.getCodePng(self.hostname)

        #登录url
        login_url = f'https://{hostname}/member.php?mod=logging&action=login&loginsubmit=yes&handlekey=ls&loginhash={loginhash}'

        #登录参数
        formData = {
            'formhash': formhash,
            'referer': f'https://{hostname}/forum.php',
            'loginfield': 'username',
            'username': self.username,
            'password': self.password,
            'questionid': '0',
            'answer': None,
            'loginsubmit': True,
            'tsdm_verify': verify
        }

        #模拟登录
        login_rst = self.session.post(login_url, proxies=self.proxies, data=formData, verify=False, headers=self.headers)

        #若在模拟登陆的响应中的html文本匹配到“回来”，则说明登录成功
        if (re.search(u'回来', login_rst.text)):
            print("登陆成功")
            self.sign(self.hostname)
            self.autoWork()
            return True
        elif(re.search(u'码', login_rst.text)):
            print("验证码错误，正在重试")
            return False
        else:
            print("账号或密码错误，请检查")
            return True

    def getCodePng(self, hostname):

        #获取验证码图片
        codePic = self.session.get(
            f'https://{hostname}/plugin.php?id=oracle:verify&time=_{int(round(time.time() * 1000))}', verify=False,
            headers=self.headers).content

        #使用ddddOCR识别验证码
        ocr = ddddocr.DdddOcr(old=True)
        res = ocr.classification(codePic)
        return res

    def sign(self, hostname):

        #获取界面url
        url = f'https://{hostname}/plugin.php?id=dsu_paulsign:sign'

        #上传签到参数url
        url1 = f'https://{hostname}/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1'

        #获取签到页html文本
        signFormText = self.session.get(url, verify=False, headers=self.headers).text

        #获取签到页面formhash
        formhash = re.search(r'<input type="hidden" name="formhash" value="(.+?)" class="scbar_hidden"/>', signFormText).group(1)

        #签到参数
        data = {
            'formhash': formhash,
            'qdxq': 'kx',
            'qdmode': 3,
            'todaysay': "",
            'fastreply': 1
        }

        #模拟签到
        res = self.session.post(url1, data=data, verify=False, headers=self.headers).text

        #输出结果
        if (re.search(u'成功', res)):
            print("签到成功!")
        else:
            print("签到失败")

    def autoWork(self):
        url = "https://www.tsdm39.net/plugin.php?id=np_cliworkdz:work"
        data1={
            'act':'clickad'
        }
        data2={
            'act':'getcre'
        }
        for i in range(6):
            self.session.post(url, verify=False, data=data1, headers=self.headers)
        res = self.session.post(url, verify=False, data=data2, headers=self.headers).text
        if(re.search(u'币', res)):
            print('打工完成')
        else:
            print('打工失败')


if __name__ == "__main__":

    username = input("请输入用户名：")

    password = input("请输入密码：")

    #创建自动签到对象实例
    instance = discuzLogin('www.tsdm39.net', username, password)

    #开始登录
    instance.userLogin('www.tsdm39.net', username, password)

    print("程序结束")
