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
