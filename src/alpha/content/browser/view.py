# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from email.mime.text import MIMEText
import json
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from zope.globalrequest import getRequest


class NewsItemView(BrowserView):
    template = ViewPageTemplateFile('templates/news_item_view.pt')
    def __call__(self):
        return self.template()


class ProductView(BrowserView):
    def pdb(self):
        request = self.request
        alsoProvides(request, IDisableCSRFProtection)
        import pdb;pdb.set_trace()

    def getImg(self):
	request = self.request
	context = self.context
	imgBrain = api.content.find(context=context, portal_type='ProductImg')
	return imgBrain

class CoverView(BrowserView):
    template = ViewPageTemplateFile('templates/cover_view.pt')
    def __call__(self):
	return self.template()
