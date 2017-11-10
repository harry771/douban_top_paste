import requests
from bs4 import BeautifulSoup
from PIL import Image
import re
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36',
    'Referer':'https://accounts.douban.com/login?alias=&redir=https%3A%2F%2Fwww.douban.com%2F&source=index_nav&error=1001'
}

# 帖子的连接
bash_urls = [
    '',
    '',
    '',
]

def login(username,passwd,url='https://accounts.douban.com/login'):
    '''
    模拟登陆豆瓣
    :param username: username
    :param passwd: passwd
    :return:
    '''
    caprcha_id,veri_code_url = verification_code(url)
    # 判断是否需要验证码
    if veri_code_url != None:
        with open('code1.jpg','wb') as f:
            f.write(requests.get(veri_code_url).content)
        try:
            img = Image.open('code1.jpg')
            img.show()
            img.close()
        except:
            print('图片打开失败')
        else:
            veri_code_input = input('输入验证码:')

    post_data = {
        'source': 'index_nav',
        'redir': 'https://www.douban.com/' ,
        'form_email': username,
        'form_password': passwd,
        'login': '登陆',
    }

    if caprcha_id != None:
        post_data['captcha-id']= caprcha_id
        post_data['captcha-solution'] = veri_code_input

    session = requests.session()
    session.post(url,data  = post_data,headers = headers)
    return session

def verification_code(url):

    '''
    判断是否需要输入验证码
    :param url: 登陆的URL
    :return:
    '''

    bsobj = BeautifulSoup(requests.get(url).text,'lxml')
    try:
        ver_code_link  =  bsobj.find('img',id='captcha_image')['src']
        caprcha_id = bsobj.find('div',{'class':'captcha_block'}).find_all('input')[1]['value']
    except BaseException:
        return None,None
    else:
        return caprcha_id,ver_code_link

def get_group_url(bash_url):
    '''
    得到小组的链接，判断是否加入小组。
    :return: group_url
    '''
    bsobj = BeautifulSoup(requests.get(bash_url,headers = headers).text,'lxml')
    group_url = bsobj.find('div',{'class':'title'}).find('a')['href']
    return group_url

def join_the_group(session,bash_url):
    '''
    判断是否加入这个小组，未加入则无法正常回帖!
    :param group_url: 小组连接
    :return:
    '''
    group_url = get_group_url(bash_url)
    bsobj = BeautifulSoup(session.get(group_url).text,'lxml')
    try:
        # 未加入小组
        join_group = bsobj.find('a', {'class': 'bn-join-group'})
        join_group_text = join_group.find('span').text
    except:
        # 已经加入小组
        in_group = bsobj.find('div',{'class':'group-misc'}).text
        print(in_group.replace(' ', '')[:-6])
    else:
        # 请求加入小组URL
        if join_group_text == '加入小组':
            session.get(join_group['href'])
            print('你已经加入小组')

def replies(session,bash_url):
    '''
    顶贴 参考 http://xhzyxed.cn/2017/11/07/%E8%B1%86%E7%93%A3%E8%87%AA%E5%8A%A8%E9%A1%B6%E8%B4%B4/#more
    :param session:
    :return:
    '''
    print('正在回帖%s'%bash_url)
    url = bash_url+'add_comment'
    ##在控制台查看顶贴的次数
    ##提交的数据
    ding_text = requests.get('http://whatthecommit.com/index.txt').text
    print(ding_text)
    data = {
        "rv_comment": ding_text,
        "ck": "aubV",
        'start': '0',
        'submit_btn': '加上去'
    }
    while True:
        rval = session.get(bash_url + '?start=5000#last', headers=headers)
        # 检验是否需要输入验证码?
        ##寻找要提交的ck参数
        data['ck'] = re.search('ck=(\w+)', rval.text).group(1)

        captcha_need = re.search('src=\"(.*captcha.*)+\"', rval.text)
        # 需要验证输入验证码
        if captcha_need != None:
            mat = re.search('src=\"(.*captcha.*)+\"', rval.text).group(1).split(' ')
            # 验证码url
            img_url = mat[0]
            # 验证码隐藏域
            captcha_id = re.split('&', img_url)[0].split('=')[1]
            if mat:
                with open('code.jpg', 'wb') as f:
                    f.write(requests.get(img_url).content)
                try:
                    img = Image.open('code.jpg')
                    img.show()
                    img.close()
                except:
                    print('图片打开失败')
                else:
                    veri_code_input = input('输入验证码:')
                    # 构造验证码提交的数据
                    ding_text = requests.get('http://whatthecommit.com/index.txt').text
                    print(ding_text)
                    data_captcha = {
                        "rv_comment": ding_text,
                        "ck": data['ck'],
                        'start': '0',
                        'submit_btn': '加上去',
                        'captcha-solution': veri_code_input,
                        'captcha-id': captcha_id
                    }
                    session.post(url=url, data=data_captcha, headers=headers)
                    break

        # 不需要验证码的时候，直接提交
        else:
            session.post(url=url, data=data, headers=headers)
            break

if __name__ == '__main__':
    douban_session = login(
        username='',
        passwd=''
    )
    for bash_url in bash_urls:
        print('正在加入%s的小组'%bash_url)
        join_the_group(douban_session,bash_url)
        time.sleep(1)
    while True:
        for url in bash_urls:
            print('正在回帖%s')
            replies(douban_session,url)
            print('等待五秒，回帖下一个URL')
            time.sleep(5)
        print('等待300秒开始下一轮回帖！')
        time.sleep(300)
