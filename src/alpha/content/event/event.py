# -*- coding: utf-8 -*-
from plone import api
from zope.globalrequest import getRequest
from alpha.content.browser.view import UpdateConfiglet
from ZPublisher.HTTPResponse import HTTPResponse
from random import randint
import pdb
import requests
import time
import datetime


def move_to_top(item, event):
    request = getRequest()
    folder = item.getParentNode()
    if not hasattr(folder, 'moveObjectsToTop'):
        return
    folder.moveObjectsToTop(item.id)
    abs_url = folder.absolute_url()
    request.response.redirect('%s/folder_contents' %abs_url)

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

def delUserPromoCodeConfiglet(event):
    username = event.principal
    existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode') or {}
    existCode = {key:val for key, val in existCode.items() if val != username}
    api.portal.set_registry_record('alpha.content.browser.user_configlet.IUser.promoCode', existCode)

def addUserToAnother(event):
    request = getRequest()
    if request.get('form.buttons.register'):
        userName = request.get('form.widgets.username', '')
        email = request.get('form.widgets.email', '')
        pwd = request.get('form.widgets.password', '')
        fullname = request.get('form.widgets.fullname', '')

        if 'alpha_cn' in request['URL']:
             url = request['URL1'].replace('alpha_cn', 'alpha_en')
        else:
             url = request['URL1'].replace('alpha_en', 'alpha_cn')

        response = requests.post(url + '/adduser', headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, 
                                json={'email': email, 'password': pwd, 'username': userName, 'fullname': fullname}, 
                                auth=('admin', '123456'))

def modifyUserToAnother(event):
    request = getRequest()
    if hasattr(event.context, 'member'):
        user = event.context.member.id
        data = event.data

        if data['promoCode']:
            existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode') or {}
            if data['promoCode'] in existCode.values():
                api.portal.show_message(message=_(u'promoCode is repeat!!'), request=getRequest(), type='error')
            existCode.update({user: data['promoCode']})
            api.portal.set_registry_record('alpha.content.browser.user_configlet.IUser.promoCode', existCode)
        if request.get('form.buttons.save'):

            if 'alpha_cn' in request['URL']:
                 requests_url = request['URL1'].replace('alpha_cn', 'alpha_en')
            else:
                 requests_url = request['URL1'].replace('alpha_en', 'alpha_cn')
            url = "{}/@users/{}".format(requests_url, user)

            response = requests.patch(url, headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                                      json= event.data,
                                      auth=('admin', '123456'))
            response = requests.post(requests_url+'/updateUserConfiglet', 
                                     headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                                     json= {'username': user, 'promoCode': data['promoCode']},
                                     auth=('admin', '123456'))

def delUserToAnother(event):
    request = getRequest()
    user = event.principal

    existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode') or {}
    existCode.pop(user, None)
    api.portal.set_registry_record('alpha.content.browser.user_configlet.IUser.promoCode', existCode)

    # check event repeat
    if request.get('form.button.Modify'):

        if 'alpha_cn' in request['URL']:
             requests_url = request['URL1'].replace('alpha_cn', 'alpha_en')
        else:
             requests_url = request['URL1'].replace('alpha_en', 'alpha_cn')
        url = "{}/@users/{}".format(requests_url, user)
        
        response = requests.post(requests_url+'/getUserProperty', headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, 
                                 json={'username': user}, auth=('admin', '123456'), timeout=30)
        if 'error' not in response.text:
            print url
            try:
                response = requests.delete(url, headers={'Accept': 'application/json'}, auth=('admin', '123456'), timeout=30)
                print response.text
            except Exception as ex:
                print ex
