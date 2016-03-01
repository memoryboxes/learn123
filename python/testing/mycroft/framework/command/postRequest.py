#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import BaseCommand
import requests
import urlparse
import json
import time
import os

class PostRequestCommand(BaseCommand):

    def __init__(self,
                 hostip,
                 postip,
                 postdata,
                 posturl,
                 postthenget = False,
                 rltname = "tmp.json",
                 rltpath = "fixtures/difffile/remote/",
                 cmd_des = "post request struct"):
        self.hostip = hostip
        self.postip = postip
        self.postdata = postdata
        self.posturl = posturl
        self.postthenget = postthenget
        self.rltname = rltname
        self.rltpath = rltpath
        super(PostRequestCommand, self).__init__(cmd_des)
        #timeout constant
        self._timeout = 10

    def execute(self):
        print '****************start test posturl******************'
        if self.postip is None:
            login_ip = self.hostip
        else:
            login_ip = self.postip
        login_url = 'http://%s/zh-cn/accounts/login/?next=/zh-cn/'%login_ip
        client = requests.session()  # 整个会话要一直使用这个client
        client.get(login_url)  # 请求登录页面，CSRFToken会更新到Cookie里
        csrftoken = client.cookies['csrftoken']
        login_data = {'username':'admin', 'password':'netis', 'csrfmiddlewaretoken': csrftoken}  # 构造登录表单
        resp = client.post(login_url, data=login_data, headers={'Referer': login_url})  # 登录。此处resp.status_code应为200

        post_url = urlparse.urljoin('http://%s'%login_ip,self.posturl)
        print post_url
        headers = {'X-CSRFToken': client.cookies['csrftoken'], 'X-Requested-With': 'XMLHttpRequest'}
        if self.postdata is None:
            resp1 = client.post(post_url, headers=headers)
        else:
            postdata = eval(self.postdata)
            postdata['csrfmiddlewaretoken'] = csrftoken
            resp1 = client.post(post_url, data=postdata, headers=headers)

        if resp1.status_code != 200:
            raise Exception('Post Request is failure,status_code is %s' % resp.status_code)
        else:
            # err_msg = json.loads(resp1.content).get('error').get('message')
            print "Post Request is successful."
            if self.postthenget:
                #new
                postcontent = json.loads(resp1.content).get('data').get('job_id')
                waitnum = 0
                while waitnum < self._timeout:
                    waitnum += 1
                    get_url = post_url + postcontent + '/?_=' + str(int(time.time() * 1000))
                    resp2 = client.get(get_url)
                    if resp2.status_code != 200:
                        raise Exception('Get Request is failure, status_code is %s' % resp2.status_code)
                        break
                    else:
                        if json.loads(resp2.content).get('data').get('isDone') == False:
                            time.sleep(1)
                            continue
                        else:
                            getcontent = json.loads(resp2.content)
                            fp = open(self.rltpath.get('rltfile_path') + os.sep + self.rltname, 'w+')
                            fp.write(json.dumps(getcontent, ensure_ascii=False, indent=4).encode('UTF-8'))
                            fp.close()
                            break
                if waitnum == self._timeout:
                    print "timeout"
                    #timeout