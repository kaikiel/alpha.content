from plone import api
from zope.globalrequest import getRequest
from alpha.content.browser.view import UpdateConfiglet
from ZPublisher.HTTPResponse import HTTPResponse
from random import randint
import pdb

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
    username = event.principal.getUserName()
    api.group.add_user(groupname="level_D", username=username)

def delUserPromoCodeConfiglet(event):
    username = event.principal
    existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode') or {}
    existCode = {key:val for key, val in existCode.items() if val != username}
    api.portal.set_registry_record('alpha.content.browser.user_configlet.IUser.promoCode', existCode)
