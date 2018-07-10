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
import json


class UserGetWishList(Service):
    def getUserWishList(self, user):
        wishList = user.getProperty('wishList')
        if wishList:
            return json.dumps(wishList.split(', '))
        else: 
            return '' 

    def reply(self):
        query = self.request.form.copy()
        if query.has_key('username'):
            queryUser = query['username']
            sm = getSecurityManager()
            if sm.checkPermission('Manage portal', self.context):
                user = api.user.get(username=queryUser)
                if user:
                    return self.getUserWishList(user)
                else:
                    raise BadRequest("username is not exist")
            else: 
                self.request.response.setStatus(401)
        elif not api.user.is_anonymous(): 
            user = api.user.get_current()
            return self.getUserWishList(user)
        else:
            self.request.response.setStatus(401)


class UserSetWishList(Service):
    def setWishList(self, user, wishItemUID):
        wishList = user.getProperty('wishList')
        checkUID = api.content.find(portal_type='Product', UID=wishItemUID)
        if len(checkUID) > 0:
            if wishList:
                wishSet = set(ast.literal_eval(wishList))
                if wishItemUID not in wishSet:
                    wishSet.add(wishItemUID)
                    wishList = str([x for x in wishSet])
                else:
                    self.request.response.setStatus(406)
                    return dict(message='Add WishList Repeat!!')
            else: 
                wishList = str([wishItemUID])
            alsoProvides(self.request, IDisableCSRFProtection)
            user.setMemberProperties(mapping={'wishList': wishList})
            self.request.response.setStatus(200)
            return dict(message='Add WishList Success!!')
        else:
            raise BadRequest("wishItemUID is not valid")

    def reply(self):
        sm = getSecurityManager()
        query = self.request.form.copy()
        if not api.user.is_anonymous():
            if query.has_key('username') and query.has_key('wishItemUID'):
                queryUser = query['username']
                wishItemUID  = query['wishItemUID']
                if sm.checkPermission('Manage portal', self.context):
                    user = api.user.get(username=queryUser)
                    if user:
                        self.setWishList(user, wishItemUID)
                    else:
                        raise BadRequest("username is not exist")
                else: 
                    self.request.response.setStatus(401)
                    return dict(message='Current account does not have permission')
            elif query.has_key('wishItemUID'):
                user  = api.user.get_current()
                wishItemUID  = query['wishItemUID']
                return self.setWishList(user, wishItemUID)
            else:
                raise BadRequest("Query string supplied is not valid")
        else: 
            self.request.response.setStatus(401)
            return dict(message='Add WishList Must Be Login!!')


class UserDeleteWishList(Service):
    def deleteWishList(self, user, wishItemUID):
        wishList = user.getProperty('wishList')
        checkUID = api.content.find(portal_type='Product', UID=wishItemUID)
        if len(checkUID) > 0:
            if wishList:
                wishSet = set(ast.literal_eval(wishList))
                wishSet.discard(wishItemUID)
                wishList = str([x for x in wishSet])
            else: 
                wishList = str([wishItemUID])
            alsoProvides(self.request, IDisableCSRFProtection)
            user.setMemberProperties(mapping={'wishList': wishList})
            return checkUID[0].Title
        else:
            raise BadRequest("wishItemUID is not valid")

    def reply(self):
        sm = getSecurityManager()
        query = self.request.form.copy()
        if not api.user.is_anonymous():
            if query.has_key('username') and query.has_key('wishItemUID'):
                queryUser = query['username']
                wishItemUID  = query['wishItemUID']
                if sm.checkPermission('Manage portal', self.context):
                    user = api.user.get(username=queryUser)
                    if user:
                        deleteTitle = self.deleteWishList(user, wishItemUID)
                        if deleteTitle:
                            self.request.response.setStatus(200)
                            return dict(message=deleteTitle)
                    else:
                        raise BadRequest("username is not exist")
                else: 
                    self.request.response.setStatus(401)
            elif query.has_key('wishItemUID'):
                user  = api.user.get_current()
                wishItemUID  = query['wishItemUID']
                return self.deleteWishList(user, wishItemUID)
            else:
                raise BadRequest("Query string supplied is not valid")
        else: 
            self.request.response.setStatus(401)
