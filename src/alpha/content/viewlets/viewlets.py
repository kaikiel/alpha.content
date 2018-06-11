# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import common as base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api


class ProductBanner(base.ViewletBase):
    def getMostView(self):
        mostView = api.content.find(portal_type='Product', b_size=8)
        return mostView

    def getSpecial(self):
        special = api.content.find(portal_type='Product', b_size=8)
        return special

    def getLatest(self):
        latest = api.content.find(portal_type='Product', b_size=8)
        return latest
