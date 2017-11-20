#coding: utf-8
import requests
import json
import base64
from conf import g_conf, g_logger


class CBeeAPI:

    _bee_url  = "https://bee.quanshi.com/ucopenapi/"
    _headers  = {"Content-Type": "application/json; charset=utf-8"}

    def __init__(self, user='', pwd='', role=None):
        try:
            self._role = 0
            self._username = "全时管理员帐号"
            self._password = "全时管理员密码"
            if g_conf.server_conf and 'bee' in g_conf.server_conf:
                if 'role' in g_conf.server_conf['bee']: self._role = g_conf.server_conf['bee']['role']
                if 'user' in g_conf.server_conf['bee']: self._username = g_conf.server_conf['bee']['user']
                if 'pwd' in g_conf.server_conf['bee']: self._password = base64.b64decode(
                    g_conf.server_conf['bee']['pwd']).decode()
            if role: self._role = role
            if user: self._username = user
            if pwd:  self._password = pwd
            self._base_param = {"username": self._username, "token": ''}

            if not self.talk("auth/token/create", username=self._username, password=self._password):
                g_logger.error("获取凭据失败")
            else:
                g_logger.info("获取凭据成功: " + self._base_param['token'])

        except Exception as e:
            g_logger.exception('beeAPI init exception: ', str(e))

    @property
    def username(self):
        return self._username

    def talk(self, cmd, **kwargs):
        try:
            params = {}
            params.update(self._base_param)
            if cmd == "auth/token/create":
                del params['token']
                params["role"] = self._role
                params['password'] = self._password
                if self._role == 2:
                    params['appId'] = 23
            elif cmd == "account/delete" or cmd == "account/getinfo" or cmd == 'account/getstatus':
                params["data"] = kwargs["username"] or self._username
            elif cmd == "nil":
                params["data"] = kwargs["nil"]
            else:
                data = {}
                for k, v in kwargs.items():
                    data[k] = v
                params["data"] = data

            response = requests.post(self._bee_url + cmd,
                                     headers=self._headers, data=json.dumps(params))
            if response.status_code != 200:
                return False, 'error:\n' + response.text

            js = json.loads(response.text)
            if js["errorCode"] == 0:
                if cmd == "auth/token/create":
                    self._base_param["token"] = js["data"]["token"]
                return True, js["data"]
            else:
                return False, cmd+': '+js['errorMessage']
        except Exception as e:
            return False, cmd+': '+str(e)

    def check_token(self):
        return self.talk("auth/token/check")

    def delete_account(self, **kwargs):  # delete_account(username="")
        return self.talk("account/delete", **kwargs)

    def create_account(self, **kwargs):
        return self.talk("account/create", **kwargs)

    def modify_account(self, **kwargs):
        return self.talk("account/update", **kwargs)

    def modify_password(self, **kwargs):
        return self.talk("account/modifypassword", **kwargs)

    def get_account_info(self, **kwargs):  # get_account_info(username="")
        return self.talk("account/getinfo", **kwargs)

    def get_account_status(self, **kwargs):
        return self.talk('account/getstatus', **kwargs)

    def disable_account(self, **kwargs):
        return self.talk("account/disable", **kwargs)

    def enable_account(self, **kwargs):
        return self.talk("account/enable", **kwargs)

    # 会自动在账号信息中的departments刚添加移入的部门.但直接修改账号信息中的departments是不行的
    # 看来是全时没有做好. 经验证,移动到的部门必须存在!
    def move_account(self, **kwargs):
        return self.talk("account/movedepartment", **kwargs)

    def create_department(self, **kwargs):
        return self.talk("department/create", **kwargs)

    def modify_department(self, **kwargs):
        return self.talk("department/update", **kwargs)

    def delete_department(self, **kwargs):
        return self.talk("department/delete", **kwargs)

    def move_department(self, **kwargs):
        return self.talk("department/move", **kwargs)

    def enum_department(self, **kwargs):
        return self.talk("department/enum", **kwargs)

    def get_userid(self, **kwargs):
        return self.talk('account/authkey/get', **kwargs)

if __name__ == '__main__':
    bee = CBeeAPI()
    #print(bee.get_userid(loginnames=['lei.zhang@geekthings.com.cn'], new='true', expireTime=-1, create='true'))
    #print(bee.check_token())
    # print(bee.create_account(loginname='administrator@geekthings.com.cn', lastname='administrator',
    #                          firstname='administrator', displayname='管理员',
    #                          departments=['国盛金控', '极盛科技', '_TMP']))
