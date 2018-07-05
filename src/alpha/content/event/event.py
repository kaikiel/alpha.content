from plone import api
from zope.globalrequest import getRequest
from alpha.content.browser.view import UpdateConfiglet
from ZPublisher.HTTPResponse import HTTPResponse
from random import randint
import pdb

def move_to_top(item, event):
    request = getRequest()
    item.moveObjectsToTop(item.id)
    abs_url = api.portal.get().absolute_url()
    request.response.redirect('%s/folder_contents' %abs_url)

def add_configlet(item, event):
    action = event.status['action']
    review_state = event.status['review_state']
    if action == 'publish' and review_state == 'published':
    	try:
	    request = getRequest()
	    item.moveObjectsToTop(item.id)
            update_configlet = UpdateConfiglet()
            update_configlet()
        except Exception as e:
	   print e
    elif action == 'retract' or action == 'reject':
        request = getRequest()
        abs_url = api.portal.get().absolute_url()
        update_configlet = UpdateConfiglet()
        update_configlet()

#to modify event,moveToTop will cause error
def modify_configlet(item, event):
    request = getRequest()
    abs_url = api.portal.get().absolute_url()
    update_configlet = UpdateConfiglet()
    update_configlet()

def toFolderContents(obj, event):
    """
    Return to Folder Contents
    """
    request = getRequest()
    try:
        folder = obj.getParentNode()
    except:
        return
    if folder == None:
        try:
            folder = api.portal.get()
        except:
            return
    elif getattr(obj, 'portal_type', None) == 'Plone Site':
        folder = obj

    if request:
        request.response.redirect('%s/folder_contents' % folder.absolute_url())

def back_to_cover(event):
    request = getRequest()
    portal = api.portal.get()
    request.response.redirect(portal.absolute_url())

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
