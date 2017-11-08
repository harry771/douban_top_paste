# douban_top_paste
python 自动登陆豆瓣，和顶贴

> 配置 帖子的连接

bash_url = ''

> 配置豆瓣 账号和密码
```python
    douban_session = login(
        username='',
        passwd=''
    )
```

如果出现验证码，则会自动弹出验证码，需要手动输入。
也可以自己加入打码平台。

加入了自动判断是否为这个小组的成员，如果不是，则加入小组。


