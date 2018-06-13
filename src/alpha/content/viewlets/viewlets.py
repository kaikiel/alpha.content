# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import common as base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api


class MainBanner(base.ViewletBase):
    def pdb(self):
        import pdb;pdb.set_trace()

    def getBannerImg(self):
        portal = api.portal.get()
        bannerImg = []
        if portal.hasObject('banner'):
            bannerImg = api.content.find(portal['banner'])
        return bannerImg


class ProductViewlet(base.ViewletBase):
    def getMostView(self):
        mostView = api.content.find(portal_type='Product', b_size=12, p_indexCategory='mostView')
        return mostView

    def getSpecial(self):
        special = api.content.find(portal_type='Product', b_size=12, p_indexCategory='special')
        return special

    def getLatest(self):
        latest = api.content.find(portal_type='Product', b_size=12, p_indexCategory='latest')
        return latest


class TimeLimitViewlet(base.ViewletBase):
    def getTimeLimit(self):
        timeLimet = api.content.find(portal_type='Product', b_size=8)
        return timeLimet


class BestSellersViewlet(base.ViewletBase):
    def getBestSellers(self):
        bestSellers = api.content.find(portal_type='Product', b_size=32, p_bestSeller=True)
        bestSellersLen = len(bestSellers)
        if bestSellersLen%2 != 0:
            bestSellers = api.content.find(portal_type='Product', b_size=(bestSellersLen-1), p_bestSeller=True)
        return bestSellers


class NewsViewlet(base.ViewletBase):
    def getNewsItem(self):
        newsItem = api.content.find(portal_type='News Item', b_size=12)
        return newsItem
