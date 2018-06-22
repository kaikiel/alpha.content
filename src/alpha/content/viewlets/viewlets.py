# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import common as base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from sets import Set
import datetime

class ProductViewlet(base.ViewletBase):
    def getMostView(self):
        mostView = api.content.find(portal_type='Product', p_indexCategory='mostView')
        return mostView

    def getSpecial(self):
        special = api.content.find(portal_type='Product', p_indexCategory='special')
        return special

    def getLatest(self):
        latest = api.content.find(portal_type='Product', p_indexCategory='latest')
        return latest


class TimeLimitViewlet(base.ViewletBase):
    def getTimeLimit(self):
        portal = api.portal.get()
        timeLimit = []
        if portal.hasObject('promotions'):
            timeLimitBrain = api.content.find(portal['promotions'], portal_type='Product')
            for item in timeLimitBrain:
                item_timeLimit = item.getObject().timeLimit
                if not(item_timeLimit and not item_timeLimit >= datetime.datetime.today()):
                    timeLimit.append(item)
        return timeLimit


class BestSellersViewlet(base.ViewletBase):
    def getBestSellers(self):
        bestSellers = api.content.find(portal_type='Product', p_bestSeller=True)
        return bestSellers


class MainBanner(ProductViewlet, TimeLimitViewlet, BestSellersViewlet):
    def pdb(self):
        import pdb;pdb.set_trace()

    def getBannerPage(self):
        portal = api.portal.get()
        bannerPage = []
        if portal.hasObject('banner'):
            bannerPage = api.content.find(portal['banner'], portal_type='Document')
        return bannerPage

    def getAllIndexProduct(self):
        allProduct = Set()
        for item in self.getMostView():
            allProduct.add(item.getObject())

        for item in self.getSpecial():
            allProduct.add(item.getObject())

        for item in self.getLatest():
            allProduct.add(item.getObject())

        for item in self.getTimeLimit():
            allProduct.add(item.getObject())

        for item in self.getBestSellers():
            allProduct.add(item.getObject())

        return allProduct
    
    def getObjectImg(self, obj):
        objectImg = api.content.find(context=obj, depth=1, b_size=4)
        return objectImg


class NewsViewlet(base.ViewletBase):
    def getNewsItem(self):
        newsItem = api.content.find(portal_type='News Item', b_size=12)
        return newsItem

    def getNewsMonth(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%B')

    def getNewsYear(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%Y')

    def getNewsDay(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%d')


class FriendLinkViewlet(base.ViewletBase):
    def getFriendLink(self):
        portal = api.portal.get()
        friendLink = []
        if portal.hasObject('friend-link'):
            friendLink = api.content.find(portal['friend-link'], portal_type='Link')
        return friendLink


class ShopCart(base.ViewletBase):
   """"""


class AccountViewlet(base.ViewletBase):
    def isAnonymous(self):
        if not api.user.is_anonymous():
            return False
        return True

    def getCurrentUser(self):
        current = api.user.get_current()
        return current

