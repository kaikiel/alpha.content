# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import implements
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
import ast


class UserGetWishList(Service):
    def reply(self):
        sm = getSecurityManager()
        query = self.request.form.copy()
        if query.has_key('username'):
            queryUser = query['username']
            if sm.checkPermission('Manage portal', self.context):
                user = api.user.get(username=queryUser)
                if user:
                    wishList = user.getProperty('wishList')
                    if wishList:
                        return ast.literal_eval(wishList)
                    else: 
                        return []
                else:
                    raise BadRequest("username is not exist")
            else: 
                self.request.response.setStatus(401)
                return
        else: 
            raise BadRequest("Query string supplied is not valid")


class UserSetWishList(Service):
    def reply(self):
        sm = getSecurityManager()
        query = self.request.form.copy()
        if query.has_key('username') and query.has_key('wishItemUID'):
            queryUser = query['username']
            wishItemUID  = query['wishItemUID']
            if sm.checkPermission('Manage portal', self.context):
                user = api.user.get(username=queryUser)
                if user:
                    wishList = user.getProperty('wishList')
                    if wishList:
                        wishSet = set(ast.literal_eval(wishList))
                        wishSet.add(wishItemUID)
                        wishList = str([x for x in wishSet])
                    else: 
                        wishList = str([wishItemUID])
                    alsoProvides(self.request, IDisableCSRFProtection)
                    user.setMemberProperties(mapping={'wishList': wishList})
                    return True
                else:
                    raise BadRequest("username is not exist")
            else: 
                self.request.response.setStatus(401)
                return
        else: 
            raise BadRequest("Query string supplied is not valid")
