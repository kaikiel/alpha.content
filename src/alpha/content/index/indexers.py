#!/usr/bin/python
# -*- coding: utf-8 -*-

from plone.indexer.decorator import indexer
from alpha.content.content.product import IProduct

@indexer(IProduct)
def product_subject(obj):
    return obj.subject

@indexer(IProduct)
def product_category(obj):
    return obj.category

@indexer(IProduct)
def product_indexCategory(obj):
    return obj.indexCategory

@indexer(IProduct)
def product_bestSeller(obj):
    return obj.bestSeller
