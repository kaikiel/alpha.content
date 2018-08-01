# -*- coding: utf-8 -*-
from plone import api
from zope.globalrequest import getRequest
from alpha.content.browser.view import UpdateConfiglet
from ZPublisher.HTTPResponse import HTTPResponse
from random import randint
import pdb
import requests

def propertiesUpdate(event):
    userid = event.context.id
    users = api.user.get_users()
    request = getRequest()
    flag = true
    for user in users:
        if event.data['promoCode'] == user.getProperty('pronoCoe'):
            api.portal.show_message(message='優惠卷號碼重複'.decode('utf-8'), request=request)
            flag = false
            break;


def move_to_top(item, event):
    request = getRequest()
    folder = item.getParentNode()
    if not hasattr(folder, 'moveObjectsToTop'):
        return
    folder.moveObjectsToTop(item.id)
    abs_url = folder.absolute_url()
    request.response.redirect('%s/folder_contents' %abs_url)

def setCookieCurrentUser(event):
    request = getRequest()
    request.response.setCookie('currentUser', api.user.get_current().getUserName())

def clearCookieCurrentUser(event):
    request = getRequest()
    request.response.setCookie('currentUser', '')

def initPromoCode(event):
    promoCode = str(randint(0,99999)).zfill(5)
    existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode') or {}
    while promoCode in existCode:
        promoCode = str(randint(0,99999)).zfill(5)
    currentUser = event.object
    if hasattr(currentUser, 'setProperties'):
        currentUser.setProperties({'promoCode':promoCode})
        existCode.update({promoCode: currentUser.getUserName()})
        api.portal.set_registry_record('alpha.content.browser.user_configlet.IUser.promoCode', existCode)

def addUserDefaultGroup(event):
    request = getRequest()
    userName = request.get('form.username', '')
    email = str(request.get('form.widgets.email', ''))
    pwd = str(request.get('form.widgets.password', ''))
    fullname = str(request.get('form.widgets.fullname', ''))

    api.group.add_user(groupname="level_D", username=userName)
    if request['URL1'].split('alpha_')[1] == 'cn':
         url = request['URL1'].replace('cn', 'en')
    else:
         url = request['URL1'].replace('en', 'cn')

    requests.post(url + '/@users', headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                   json={'email': email, 'fullname': fullname, 'password': pwd, 'roles': ['Member'], 'username': userName},
                   auth=('admin', '123456'))


def delUserPromoCodeConfiglet(event):
    username = event.principal
    existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode') or {}
    existCode = {key:val for key, val in existCode.items() if val != username}
    api.portal.set_registry_record('alpha.content.browser.user_configlet.IUser.promoCode', existCode)


