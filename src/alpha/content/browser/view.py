# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.contenttypes.browser.folder import FolderView
from alpha.content import _
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.utils import getToolByName
from zope.globalrequest import getRequest
from Acquisition import aq_inner
from Products.CMFPlone.PloneBatch import Batch
from email.mime.text import MIMEText
from plone.app.users.browser.register import RegistrationForm
from alpha.content.browser.configlet import IDict
from alpha.content.browser.base_inform_configlet import IInform
from alpha.content.browser.user_configlet import IUser
from email.mime.text import MIMEText
from collections import defaultdict
from sets import Set
import ast
import json
import datetime
import requests
from db.connect.browser.views import SqlObj
import xlsxwriter
from StringIO import StringIO


class GeneralMethod(BrowserView):
    userConfirmStr = _(u'The login name you selected is already in use or is not valid. Please choose another.')
    promoCodeStr = _(u'promoCode is repeat!!')
    emailStr = _(u'Email is repeat!!')
    pwVaild = _(u'password just only Letter and Number. Minimum 5 characters.')
    pwConfirm = _(u'Passwords do not match.')

    def getLanguage(self):
        return self.context.restrictedTraverse('@@plone_portal_state').language()
    
    def getRootPathname(self):
        rootPath = api.portal.get().absolute_url_path().split('/')[1]
        return rootPath

    def salePrice(self, obj):
        permissions = api.user.get_permissions().get('Manage Site', False)
        currentGroups = api.user.get_current().getProperty('group')

        if (obj.getParentNode().id == 'promotions'):
            obj_timeLimit = obj.timeLimit or datetime.datetime(1,1,1,0,0)
            if not(obj_timeLimit and not obj_timeLimit >= datetime.datetime.today()):
                return obj.salePrice
            else:
                if api.user.is_anonymous():
                    return obj.price
                elif currentGroups == 'level_D':
                    return obj.price

        if api.user.is_anonymous():
            return obj.price

        if permissions:
            return obj.salePrice

        groupList = ['level_A', 'level_B', 'level_C', 'level_D']
        groupDict = {'level_A': 'l_a_price', 'level_B': 'l_b_price', 'level_C': 'l_c_price', 'level_D': 'salePrice'}
        for group in groupList:
            if group in currentGroups:
                return getattr(obj, groupDict[group]) or obj.salePrice

        return obj.price

    def hasSale(self):
        permissions = api.user.get_permissions().get('Manage Site', False)
        if api.user.is_anonymous():
            return False
        if permissions:
            return True

        groupList = ['level_A', 'level_B', 'level_C', 'level_D']
        groupDict = {'level_A': False, 'level_B': False, 'level_C': False, 'level_D': True}
        currentGroups = api.user.get_current().getProperty('group')
        for group in groupList:
            if group in currentGroups:
                return groupDict[group]
        return False

    def hasCheckOut(self):
        if api.user.is_anonymous():
            return True

        groupList = ['level_A', 'level_B', 'level_C', 'level_D']
        groupDict = {'level_A': False, 'level_B': False, 'level_C': True, 'level_D': True}
        currentGroups = api.user.get_current().getProperty('group')
        for group in groupList:
            if group in currentGroups:
                return groupDict[group]
        return True

    def hasPromoCode(self):
        if api.user.is_anonymous():
            return True

        groupList = ['level_A', 'level_B', 'level_C', 'level_D']
        groupDict = {'level_A': False, 'level_B': False, 'level_C': False, 'level_D': True}
        currentGroups = api.user.get_current().getProperty('group')
        for group in groupList:
            if group in currentGroups:
                return groupDict[group]
        return True

    def hasBonus(self):
        if api.user.is_anonymous():
            return False

        groupList = ['level_A', 'level_B', 'level_C', 'level_D']
        groupDict = {'level_A': False, 'level_B': False, 'level_C': True, 'level_D': True}
        currentGroups = api.user.get_current().getProperty('group')
        for group in groupList:
            if group in currentGroups:
                return groupDict[group]
        return False


class GetProductData(GeneralMethod):
    def __call__(self):
        try:
            request = self.request
            uid = request.get('uid', '')
            if uid:
                content = api.content.get(UID=uid)
                title = content.title
                contentUrl = content.absolute_url()
                price = self.salePrice(content)
                img = contentUrl + '/@@images/cover/thumb'
                data = [str(title), contentUrl, price, img]
                return json.dumps(data)
            else:
                return 'error'
        except Exception as e:
            print 'restful getProductData error {}'.format(e)


class Companys(BrowserView):
    template = ViewPageTemplateFile('templates/companys.pt')
    def __call__(self):
	return self.template()

    def getCompany(self):
        companyBrains = api.content.find(context=self.context, portal_type='Company', sort_on="getObjPositionInParent")
        orderDict = defaultdict(list)
        for com in companyBrains:
            city = com.getObject().cityCategory
            orderDict[city].append(com)
	return orderDict

    def getCityName(self, i):
        citys = [_(u'Taipei')  , (u'New Taipei'), _(u'Taoyuan') , _(u'Hsinchu')   , _(u'Miaoli'),
                 _(u'Taichung'), (u'Changhua')  , _(u'Yunlin')  , _(u'Chiayi')    , _(u'Nantou'), 
                 _(u'Tainan')  , (u'Kaohsiung') , _(u'Pingtung'), _(u'Yilan')     , _(u'Hualien'),
                 _(u'Taitung') , (u'Penghu')    , _(u'Kinmen')  , _(u'Lienchiang') ]
        try:
            
            i = int(i)-1
            name = citys[i]
            return name
        except Exception as ex:
            return


class ReturnProduct(BrowserView):
    template = ViewPageTemplateFile('templates/return_product.pt')
    def __call__(self):
        self.viewTitle = _(u'Return')
	request = self.request
	first_name = request.get('first_name')
 	last_name = request.get('last_name')
        phone = request.get('phone')
        product_name = request.get('product_name')
        product_code = request.get('product_code')
        date = request.get('date')
        opened = request.get('opened')
        order_id = request.get('order_id')
        reason = request.get('reason')
        amount = request.get('amount')
        detail = request.get('detail')

	if first_name and last_name:
	    body_str = """fisrst_name:%s<br>last_name:%s<br>phone:%s<br>date:%s<br>order_id:%s<br>product_name:%s<br>product_code:%s<br>
			amount:%s<br>reason:%s<br>opened:%s<br>detail:%s<br>
                    """ %(first_name, last_name, phone, date, order_id, product_name, product_code, amount, reason, opened, detail)
            mime_text = MIMEText(body_str, 'html', 'utf-8')
            r_email = api.portal.get_registry_record('r_email' , interface=IInform) or ''
            api.portal.send_email(
                recipient=r_email,
                sender="service@kireistar.com",
                subject="退貨申請" ,
               body=mime_text.as_string(),
            )
        return self.template()


class Brands(BrowserView):
    template = ViewPageTemplateFile('templates/brands.pt')
    def __call__(self):
        self.viewTitle = _('Brands')
	brandList = {}
	productBrains = api.content.find(context=api.portal.get()['products'], portal_type='Product')
	for item in productBrains:
            obj = item.getObject()
            brand = obj.brand
	    firstLetter = brand[0]
	    if brandList.has_key(firstLetter):
                if brand not in brandList[firstLetter]:
                    brandList[firstLetter].append(brand)
	    else:
	        brandList[firstLetter] = [brand]
	self.brandList = brandList
	return self.template()


class SiteMap(BrowserView):
    template = ViewPageTemplateFile('templates/site_map.pt')
    def __call__(self):
        self.viewTitle = _(u'Site Map')
	site_map = api.content.find(context=api.portal.get(), depth=1)
	self.site_map = site_map
        return self.template()


class NewsItemView(BrowserView):
    def getNewsMonth(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%B')

    def getNewsYear(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%Y')

    def getNewsDay(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%d')


class ProductView(GeneralMethod):
    def getImg(self):
        imgList = []
        imgNameList = ['img1', 'img2', 'img3', 'img4']
        for imgName in imgNameList:
            if getattr(self.context, imgName):
                imgList.append('{}/@@images/{}'.format( self.context.absolute_url(), imgName) )
	return imgList


class CoverView(BrowserView):
    template = ViewPageTemplateFile('templates/cover_view.pt')
    def __call__(self):
	return self.template()


class UpdateConfiglet():
    def __call__(self):
	portal = api.portal.get()
        try:
            request = self.request
        except:
            request = getRequest()

	try:
	    lang = request.cookies.get('I18N_LANGUAGE')
	    if lang == 'zh-tw':
                productBrains = api.content.find(context=portal['zh-tw']['products'], portal_type="Product")
	    elif lang == 'en-us':
		productBrains = api.content.find(ccontext=portal['en-us']['products'], protal_type='Product')
        except:
            productBrains = []
        alsoProvides(request, IDisableCSRFProtection)
        # sortList[buggy] = [0,{'1/4': 0, '1/8': 5} ]
        # sortList[${cayegory}] = [${category_count}, { ${subject}: ${subject_count} }]
        sortList = {}
	brandList = {}
        try:
            for item in productBrains:
		obj = item.getObject()
                category = obj.category
                subject = obj.subcategory
		brand = obj.brand
		title = obj.title
		productNo = obj.productNo
		objAbsUrl = obj.absolute_url()
		salePrice = obj.salePrice
		price = obj.price
		description = obj.description

                if sortList.has_key(category):
                    sortList[category][0] += 1
                    if sortList[category][1].has_key(subject):
                        sortList[category][1][subject] += 1
                    else:
                        sortList[category][1][subject] = 1
                else:
                    sortList[category] = [1, {subject: 1}]

		if brandList.has_key(brand):
		    brandList[brand] += 1
		else:
		    brandList[brand] = 1
            sortList = json.dumps(sortList).decode('utf-8')
            api.portal.set_registry_record('sortList', sortList, interface=IDict)

	    brandList = json.dumps(brandList).decode('utf-8')
	    api.portal.set_registry_record('brandList', brandList, interface=IDict)

        except  Exception as e:
            print e


class ConfirmCart(GeneralMethod):
    template = ViewPageTemplateFile("templates/confirm_cart.pt")
    i18nString = {
                 'max_bonus':_(u'The highest available bonus is'),
                 'avilable_bonus': _(u'Exceeding available bonus points'),
                 'time_passed': _(u'Time-limited product time has passed'),
                 'out_of_stock': _(u'Out of stock'),
                 'only_left': _(u'only left with'),
                 }
    def __call__(self):
        self.viewTitle = _(u'Confirm Cart')
        self.bonusMoney = api.portal.get_registry_record('alpha.content.browser.weight_configlet.IWeight.bonus')
        request = self.request
	abs_url = api.portal.get().absolute_url()
	cookie_shop_cart = request.cookies.get('shop_cart')
	if not cookie_shop_cart or not json.loads(cookie_shop_cart):
	    api.portal.show_message(message='Shop Cart Is Empty', request=request, type='warn')
	    request.response.redirect('%s/products' %abs_url)
	    return

	shop_cart = json.loads(request.cookies['shop_cart'])
	uidList = shop_cart.keys()
	productData = []
	totalNumber = 0
	for uid in uidList:
	    product = api.content.get(UID=uid)
            if product:
	        amount = int(shop_cart[str(uid)])
                totalNumber += self.salePrice(product) * amount

	        productData.append( {product: amount} )
	self.totalNumber = totalNumber
	self.productData = productData
	return self.template()

    def getUserProperties(self):
        user = api.user.get_current()
        propertyList = ['city', 'fax', 'group', 'zip', 'address2', 'address1', 'company', 'promoCode', 'telephone', 'lName', 'state', 'fName', 'country', 'fullname', 'newsletter', 'email']
        propertyDict = {}
        for p_name in propertyList:
            propertyDict.update({p_name: user.getProperty(p_name)})
        return propertyDict

    def getUsableBonus(self):
        user = api.user.get_current()
        execSql = SqlObj()
        execStr = """SELECT * FROM bonus_history WHERE `username` LIKE '%s'""" % user.getUserName()
        results = execSql.execSql(execStr)
        usable_bonus = 0
        for result in results:
            usable_bonus += result['all_bonus']
        return usable_bonus

    def getFreeShipping(self):
        free_shipping = api.portal.get_registry_record('alpha.content.browser.weight_configlet.IWeight.free_shipping')
        return free_shipping


class CountShippingFee(BrowserView):
    def __call__(self):
        request = self.request
        weight = request.form.get('weight', '')
        if weight:
            weight = round(float(weight))
            shipping_fee = api.portal.get_registry_record('alpha.content.browser.weight_configlet.IWeight.shipping_fee')
            weightList = shipping_fee.keys()
            weightList.sort(reverse=True)
            for w in weightList:
                if weight >= w:
                    return json.dumps({'shipping_fee':shipping_fee[w]})
                    
            return json.dumps({'shipping_fee':0})
        return json.dumps({'error':'without weight parameter'})


class DownloadExcel(GeneralMethod):

    def __call__(self):
        output = StringIO()
        request = self.request
        productData = self.request.cookies.get('shop_cart', '')
        if productData:
            productData = json.loads(productData)
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Sheet1')

            worksheet.write('A1', '商品名稱')
            worksheet.write('B1', '料號')
            worksheet.write('C1', '價格')
            worksheet.write('D1', '數量')
            worksheet.write('E1', '總價')

            count = 2
            totalPrice = 0
            for k,v in productData.items():
                obj = api.content.get(UID=k)
                price = self.salePrice(obj)
                worksheet.write('A%s' %count, obj.title)
                worksheet.write('B%s' %count, obj.productNo)
                worksheet.write('C%s' %count, price)
                worksheet.write('D%s' %count, int(v))
                worksheet.write('E%s' %count, price * int(v))
                totalPrice += price * int(v)
                count += 1
            worksheet.write('A%s' %count, '總金額')
            worksheet.write('B%s' %count, totalPrice)

            workbook.close()

            response = request.response
            response.setHeader('Content-Type', 'application/xls')
            response.setHeader('Content-Disposition', 'attachment; filename="shopping_list.xls"' )
            request.response.setCookie('shop_cart', '')
            #api.portal.show_message(message='訂單已成立，之後會用email聯絡'.encode('utf-8'), request=request)
            response.appendBody(output.getvalue())
            response.outputBody()
        return 


class DelPromoQty(BrowserView):
    def __call__(self):
        request = self.request
        uid = request.get('uid', '')
        order_qty = request.get('qty', '')
        product = api.content.get(UID=uid)
        if product:
            alsoProvides(request, IDisableCSRFProtection)
            qty = product.limit_qty
            qty = qty - int(order_qty)
            product.limit_qty = qty if qty > 0 else 0


class UseCoupon(BrowserView):
    def __call__(self):
        request = self.request
        execSql = SqlObj()
        dateStr = datetime.datetime.now().strftime('%Y%m%d%H%M%S%z');
        order_id       = 'Order-{}'.format(dateStr)
        billing_no     = request.get('billing_no', '')
        payment        = request.get('payment', '')
        username       = api.user.get_current().getUserName()
        recipient_name = request.get('recipient_name', '')
        email          = request.get('email', '')
        phone          = request.get('phone', '')
        address        = request.get('address', '')
	currency       = request.get('currency')
        disc_price     = request.get('disc_price') or 'Null'
        disc_bonus     = request.get('disc_bonus') or 'Null'
        shipping       = request.get('shipping') or 'Null'
	total          = request.get('total')

        # {"total":"XX","currency":"XX","details":{"subtotal":"XX","tax":"XX","shipping":"XX","shipping_discount":"-XX"}}
        amount         = request.get('amount', '')
        # [{"name":"XX","price":"XX","currency":"XX","quantity":1, "description":"{"disc_price":0,"bonus":0,"rebate":0}"},]
        items          = request.get('items', '')
        # order data from paypal after check out
        rep            = request.get('rep', '')
	create_time    = request.get('create_time')
        coupon_owner   = ''
	coupon_code    = request.get('coupon_code') or 'Null'
        if coupon_code and coupon_code != 'Null':

            existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode')
            coupon_owner = ', '.join([key for key, value in existCode.items() if value == coupon_code]) 


        execStr = "INSERT INTO `coupon_status`( \
                   `order_id`, `billing_no`, `coupon_code`, `coupon_owner`, `user`, `recipient_name`, \
                   `email`, `phone`, `address`, `currency`, `disc_bonus`, `disc_price`, `shipping`, `total`, `time`) \
                   values ('%s', '%s', %s, '%s', '%s', '%s', \
                           '%s', '%s', '%s', '%s', %s, %s, %s, %s, '%s')" \
                   %(order_id, billing_no, coupon_code, coupon_owner, username, recipient_name, \
                     email, phone, address, currency, disc_bonus, disc_price, shipping, total, create_time)
        execSql.execSql(execStr)

        if not api.user.is_anonymous():      
            bonus = int(request.get('bonus', 0))
            try:
                if bonus > 0:
                    execSql = SqlObj()
                    execStr = """SELECT * FROM bonus_history WHERE `username`='%s' AND `bonus_status`=1""" %username
                    results = execSql.execSql(execStr)
                    for result in results:
                        id = result['id']
                        usable_bonus = result['all_bonus'] 
                        used_bonus = result['used_bonus']
                        uni_bonus = result['uni_bonus']
                        status = result['bonus_status']
                        
                        if status == 1:
                            last_bonus = bonus - usable_bonus
                            used = usable_bonus - bonus
                            used_bonus = used_bonus + (used if used >=0 else usable_bonus)
                            usable_bonus = used if used >=0 else 0
                            status = 2 if usable_bonus <= 0 else 1
                            bonus = last_bonus if last_bonus >= 0 else 0
                            
                            execSql = SqlObj()
                            execStr = "UPDATE bonus_history  SET all_bonus = %s, used_bonus = %s, bonus_status = %s WHERE `id` = %s" \
                                       %(usable_bonus, used_bonus, status, int(id))
                            results = execSql.execSql(execStr)

                        if bonus <= 0:
                            break
            except Exception as ex:
                import pdb;pdb.set_trace()

        if items:
            items = json.loads(items)
            for item in items:
                execSql = SqlObj()
                name         = item.get('name', '')
                qty          = item.get('quantity', 0)
                price        = float(item.get('price', 0))
                description  = json.loads(item.get('description', ''))
                disc_price   = float(description['disc_price'])
                bonus        = description['bonus'] if not api.user.is_anonymous() else 0
                rebate       = float(description['rebate'])
                bonus_status = 1 if bonus > 0 else 0
                all_bonus = qty * bonus
                execStr = "INSERT INTO bonus_history ( \
                           `order_id`, `username`, `date`, `product_name`, `qty`, `currency`, `price`, `disc_price`, \
                           `uni_bonus`, `all_bonus`, `bonus_status`, `coupon_owner`, `rebate`, `rebate_status`) \
                           values ('%s', '%s', '%s', '%s', %s, '%s', %s, %s, \
                                    %s ,  %s ,  %s , '%s', %s,  %s)" \
                           %(order_id, username, create_time, name, qty, currency, price, disc_price, \
                             bonus, all_bonus, bonus_status, coupon_owner, rebate, 1)
                results = execSql.execSql(execStr)

            self.sendCoustomerEmail(recipient_name, email, address, order_id, create_time, items, amount)
            self.sendAdminEmail(recipient_name, email, address, order_id, create_time, items, amount)

            if coupon_owner:
                try:
                    self.sendPromoCodeOwnerEmail(coupon_owner, order_id, create_time, items, currency)
                except Exception as e:
                    import pdb;pdb.set_trace()

    def sendPromoCodeOwnerEmail(self, owner, order_id, date, items, currency):
        request = self.request
        itemsList = []
        rebate_total = 0
        for item in items:
            name         = item.get('name', '')
            qty          = item.get('quantity', 0)
            description  = json.loads(item.get('description', ''))
            rebate       = float(description['rebate'])
            if rebate > 0:
                itemStr = """ \
                            <tr>\
                              <td align="center" style="border: 1px solid black;">{0}</td>\
                              <td align="center" style="border: 1px solid black;">{1}</td>\
                              <td align="center" style="border: 1px solid black;">{3}{2}</td>\
                            </tr>\
                          """.format(name, qty, rebate, currency)
                rebate_total += rebate
                itemsList.append(itemStr)
        if rebate_total > 0:
            itemsList = ''.join(itemsList)
            owners = owner.split(', ')
            for owner in owners:
                user = api.user.get(username=owner)
                email = user.getProperty('email')
                url = self.context.portal_url() + '/rebate_history'
                description = 'There is an order to use your coupon code and you will get a {}{} rebate'.format(currency, rebate_total)
                body_str = """<table style="width:80%;">\
                                <tr>\
                                  <td colspan="2">\
                                    <p>Hi {0}:<p>\
                                    <span>&nbsp;&nbsp;&nbsp;&nbsp;{1}</span>\
                                  </td>\
                                </tr>\
                                <tr style="height:1.5em;"></tr> \
                                <tr>\
                                  <td>{2}</td>\
                                  <td style="text-align: right;">{3}</td>\
                                </tr>\
                                <tr>\
                                  <td colspan="2" align="center">\
                                    <table class="items" style="border-collapse: collapse;  min-width:80%;">\
                                      <tr>\
                                        <th align="center" style="border: 1px solid black;">name</th>\
                                        <th align="center" style="border: 1px solid black;">qty</th>\
                                        <th align="center" style="border: 1px solid black;">rebate</th>\
                                      </tr>\
                                        {4}\
                                      <tr>\
                                        <td colspan="3" align="right">total : {7}{5}</td>\
                                      </tr>\
                                    </table>
                                  </td>\
                                </tr>\
                                <tr>\
                                  <td colspan="2"><a href="{6}">{6}</a></td>\
                                </tr>\
                                <tr style="height:1.5em;"></tr> \
                                <tr style="height:1.5em;"></tr> \
                                <tr><td colspan="2" align="right">Kireistar</td></tr> \
                              </table>\
                           """.format(owner, description, order_id, date, itemsList, rebate_total, url, currency)
                mime_text = MIMEText(body_str, 'html', 'utf-8')
                r_email = api.portal.get_registry_record('r_email' , interface=IInform) or ''
                api.portal.send_email(
                    recipient=email,
                    sender="service@kireistar.com",
                    subject=_(u"Thanks for your recommend!"),
                    body=mime_text.as_string(),
                )
                api.portal.show_message(message='發送成功!'.decode('utf-8'), request=request)

    def sendAdminEmail(self, username, email, address, order_id, date, items, amount):
        request = self.request

        # {"total":"XX","currency":"XX","details":{"subtotal":"XX","tax":"XX","shipping":"XX","shipping_discount":"-XX"}}
        amount = json.loads(amount)
        total = amount.get('total', '')
        currency = amount.get('currency', '')
        details = amount.get('details', '')
        subtotal      = details.get('subtotal', '')
        shipping      = details.get('shipping', '')
        shipping_disc = details.get('shipping_discount', '')

        itemsList = []
        for item in items:
            name         = item.get('name', '')
            qty          = item.get('quantity', 0)
            description  = json.loads(item.get('description', ''))
            price        = item.get('price', '')
            itemStr = """ \
                        <tr>\
                          <td align="center" style="border: 1px solid black;">{0}</td>\
                          <td align="center" style="border: 1px solid black;">{1}</td>\
                          <td align="center" style="border: 1px solid black;">{3}{2}</td>\
                        </tr>\
                      """.format(name, qty, price, currency)
            itemsList.append(itemStr)
        itemsList = ''.join(itemsList)
        

        description = _(u'Kireistar have a new Order {}, Total Price are {} {}.').format(order_id, currency, total)
        body_str = """<table style="width:80%;">\
                        <tr>\
                          <td colspan="2">\
                            <p>{0}'s order:<p>\
                            <span>&nbsp;&nbsp;&nbsp;&nbsp;{1}</span>\
                          </td>\
                        </tr>\
                        <tr style="height:1.5em;"></tr> \
                        <tr>\
                          <td colspan="2">{4}</td>\
                        </tr>\
                        <tr>\
                          <td colspan="2">{5}</td>\
                        </tr>\
                        <tr>\
                          <td>{2}</td>\
                          <td style="text-align: right;">{3}</td>\
                        </tr>\
                        <tr>\
                          <td colspan="2" align="center">\
                            <table class="items" style="border-collapse: collapse;  min-width:80%;">\
                              <tr>\
                                <th align="center" style="border: 1px solid black;">name</th>\
                                <th align="center" style="border: 1px solid black;">qty</th>\
                                <th align="center" style="border: 1px solid black;">price</th>\
                              </tr>\
                                {6}\
                              <tr>\
                                <td colspan="3" align="right">Sub Total : {11}{7}</td>\
                              </tr>\
                              <tr>\
                                <td colspan="3" align="right">Discount : {11}{8}</td>\
                              </tr>\
                              <tr>\
                                <td colspan="3" align="right">Shipping Fee : {11}{9}</td>\
                              </tr>\
                              <tr>\
                                <td colspan="3" align="right">Total : {11}{10}</td>\
                              </tr>\
                            </table>
                          </td>\
                        </tr>\
                        <tr style="height:1.5em;"></tr> \
                        <tr style="height:1.5em;"></tr> \
                        <tr><td colspan="2" align="right">Kireistar</td></tr> \
                      </table>\
                   """.format(username, description, order_id, date, address, email, itemsList, subtotal, shipping_disc, shipping, total, currency)
        mime_text = MIMEText(body_str, 'html', 'utf-8')
        r_email = api.portal.get_registry_record('r_email' , interface=IInform) or ''
        api.portal.send_email(
            recipient=r_email,
            sender="service@kireistar.com",
            subject=_(u"Kireistar have a new order {}").format(order_id),
            body=mime_text.as_string(),
        )
        api.portal.show_message(message='發送成功!'.decode('utf-8'), request=request)

    def sendCoustomerEmail(self, username, email, address, order_id, date, items, amount):
        request = self.request

        # {"total":"XX","currency":"XX","details":{"subtotal":"XX","tax":"XX","shipping":"XX","shipping_discount":"-XX"}}
        amount = json.loads(amount)
        total = amount.get('total', '')
        currency = amount.get('currency', '')
        details = amount.get('details', '')
        subtotal      = details.get('subtotal', '')
        shipping      = details.get('shipping', '')
        shipping_disc = details.get('shipping_discount', '')

        itemsList = []
        for item in items:
            name         = item.get('name', '')
            qty          = item.get('quantity', 0)
            description  = json.loads(item.get('description', ''))
            price        = item.get('price', '')
            itemStr = """ \
                        <tr>\
                          <td align="center" style="border: 1px solid black;">{0}</td>\
                          <td align="center" style="border: 1px solid black;">{1}</td>\
                          <td align="center" style="border: 1px solid black;">{3}{2}</td>\
                        </tr>\
                      """.format(name, qty, price, currency)
            itemsList.append(itemStr)
        itemsList = ''.join(itemsList)
        

        description = _(u'thanks for your order, we hope you enjoyed shopping with us.')
        body_str = """<table style="width:80%;">\
                        <tr>\
                          <td colspan="2">\
                            <p>Hi {0}:<p>\
                            <span>&nbsp;&nbsp;&nbsp;&nbsp;{1}</span>\
                          </td>\
                        </tr>\
                        <tr style="height:1.5em;"></tr> \
                        <tr>\
                          <td colspan="2">{4}</td>\
                        </tr>\
                        <tr>\
                          <td colspan="2">{5}</td>\
                        </tr>\
                        <tr>\
                          <td>{2}</td>\
                          <td style="text-align: right;">{3}</td>\
                        </tr>\
                        <tr>\
                          <td colspan="2" align="center">\
                            <table class="items" style="border-collapse: collapse;  min-width:80%;">\
                              <tr>\
                                <th align="center" style="border: 1px solid black;">name</th>\
                                <th align="center" style="border: 1px solid black;">qty</th>\
                                <th align="center" style="border: 1px solid black;">price</th>\
                              </tr>\
                                {6}\
                              <tr>\
                                <td colspan="3" align="right">Sub Total : {11}{7}</td>\
                              </tr>\
                              <tr>\
                                <td colspan="3" align="right">Discount : {11}{8}</td>\
                              </tr>\
                              <tr>\
                                <td colspan="3" align="right">Shipping Fee : {11}{9}</td>\
                              </tr>\
                              <tr>\
                                <td colspan="3" align="right">Total : {11}{10}</td>\
                              </tr>\
                            </table>
                          </td>\
                        </tr>\
                        <tr style="height:1.5em;"></tr> \
                        <tr style="height:1.5em;"></tr> \
                        <tr><td colspan="2" align="right">Kireistar</td></tr> \
                      </table>\
                   """.format(username, description, order_id, date, address, email, itemsList, subtotal, shipping_disc, shipping, total, currency)
        mime_text = MIMEText(body_str, 'html', 'utf-8')
        r_email = api.portal.get_registry_record('r_email' , interface=IInform) or ''
        api.portal.send_email(
            recipient=email,
            sender="service@kireistar.com",
            subject=_(u"Thanks for your order!"),
            body=mime_text.as_string()
        )
        api.portal.show_message(message='發送成功!'.decode('utf-8'), request=request)



class ContactUs(BrowserView):
    template = ViewPageTemplateFile('templates/contact_us.pt')
    def __call__(self):
        self.viewTitle = _(u'Contact Us')
	self.address = api.portal.get_registry_record('address', interface=IInform)
	self.cellphone = api.portal.get_registry_record('cellphone', interface=IInform)

        request = self.request
	name = request.get('name', '')
	email = request.get('email', '')
	message = request.get('message', '')
        if name and email and message:
            body_str = """Name:{}<br/>Email:{}<br/>Message:{}""".format(name, email, message)
            mime_text = MIMEText(body_str, 'html', 'utf-8')
            r_email = api.portal.get_registry_record('r_email' , interface=IInform) or ''
            api.portal.send_email(
                recipient=r_email,
                sender="service@kireistar.com",
                subject="Contact Us From {}".format(name),
                body=mime_text.as_string(),
            )
            api.portal.show_message(message='發送成功!'.decode('utf-8'), request=request)

	return self.template()


class NewsFolderView(FolderView, NewsItemView):
    def results (self, **kwargs):
        kwargs.update(self.request.get('contentFilter', {}))
        if 'object_provides' not in kwargs:  # object_provides is more specific
            kwargs.setdefault('portal_type', 'News Item')
        kwargs.setdefault('batch', True)

        listing = aq_inner(self.context).restrictedTraverse(
            '@@folderListing', None)
        if listing is None:
            return []
        results = listing(**kwargs)
        return results


class SocialButtonMacro(BrowserView):
    """"""


class SendMail(BrowserView):
    def __call__(self):
        request = self.request
	name = request.get('name')
	email = request.get('email')
	message = request.get('message')
        body_str = """Name:{}<br/>Email:{}<br/>Message:{}""".format(name, email, message)
        mime_text = MIMEText(body_str, 'html', 'utf-8')
        r_email = api.portal.get_registry_record('r_email' , interface=IInform) or ''
        api.portal.send_email(
            recipient=r_email,
            sender="service@kireistar.com",
            subject="Contact Us From {}".format(name),
            body=mime_text.as_string(),
        )
        api.portal.show_message(message='發送成功!'.decode('utf-8'), request=request)


class CompareList(GeneralMethod):
    template = ViewPageTemplateFile('templates/compare_list.pt')
    def __call__(self):
        self.viewTitle = _(u'Compare List')
	request = self.request
	json_compare_list = request.cookies.get('compare_list')
	data = []
	if json_compare_list:
	    compare_list = json.loads(json_compare_list)
	    for item in compare_list:
	        contents = api.content.find(UID = item)
 	        for brain in contents:
	            data.append(brain)
	    self.data = data
	else:
	    self.data = False

	return self.template()


class LogOut(BrowserView):
    def __call__(self):
        mt = getToolByName(self.context, 'portal_membership')
        mt.logoutUser(self.request)
        current_url = self.context.portal_url() 
        self.request.response.redirect(current_url)


class Register(GeneralMethod):
    template = ViewPageTemplateFile('templates/register_form.pt')
    def __call__(self):
        request = self.request

        if request.form.get('widget-form-btn', '') == 'widget-form-btn':
            self.registerUser()
            if self.checkAdmin():
                return self.request.response.redirect(self.context.portal_url()+'/@@usergroup-userprefs')
            return

        username = request.form.get('username', '')
        if username:
            return self.checkUsername()

        email = request.form.get('email', '')
        if email:
            return self.checkEmail()

        promoCode = request.form.get('promoCode', '')
        if promoCode:
            return self.checkPromoCode()

        return self.template()

    def checkAdmin(self):
        return api.user.get_permissions().get('Manage Site', False)

    def checkUsername(self):
        request = self.request
        username = request.form.get('username', '')
        if username:
            user = api.user.get(username=username)
            if user:
                return "0"
            else: 
                return "1"

    def checkEmail(self):
        request = self.request
        email = request.form.get('email', '')
        userid = request.form.get('id_email', '')
        if email:
            emailList = [user.getProperty('email') for user in api.user.get_users()]
            if userid:
                current_user = api.user.get(username=userid)
                user_email = current_user.getProperty('email')
                if email == user_email:
                    return "1"
            if email in emailList:
                return "0"
            else: 
                return "1"

    def checkPromoCode(self):
        request = self.request
        existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode') or {}
        promoCode = request.form.get('promoCode', '')
        if promoCode:
            if promoCode in existCode.values():
                return "0"
            else: 
                return "1"

    def registerUser(self):
        request = self.request
        
        propertyList = ['fName', 'lName', 'telephone', 'fax', 'country', 'state', 'city', 'zip', 'address1', 'address2', 'company', 'group', 'newsletter']
        if self.checkAdmin():
            propertyList.append('promoCode')
        if request.form.get('widget-form-btn', '') == 'widget-form-btn':
            propertyDict={}
            for property in propertyList:
                value = request.form.get(property, '')
                if value:
                    propertyDict.update({property: value})
                    if property == 'newsletter':
                        self.updateEmailList(request.form.get('email', ''), value)
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            email    = request.form.get('email', '')
            propertyDict.update({'fullname': request.form.get('lName', '') + ' ' + request.form.get('fName', '')})
            user = api.user.create(username=username, email=email, password=password, properties=propertyDict)

    def updateEmailList(self, email, action):
        newsletter = self.getNewsletter()
        emailList = Set()
        if newsletter != None:
            emailList = newsletter.getObject().description.split('\r\n')
            emailList = Set([e for e in emailList if e != ''])
            if action == 'true':
                emailList.add(email)
            elif action == 'false':
                emailList.discard(email)
            request = self.request
            alsoProvides(request, IDisableCSRFProtection)
            emailStr = ''
            for email in emailList:
                emailStr += email + '\r\n'
            newsletter.getObject().description = emailStr

    def getNewsletter(self):
        portal = api.portal.get()
        if portal.hasObject('resource'):
            emailPage = api.content.find(portal['resource'], portal_type='Document', id='newsletter' )
            return emailPage[0] if len(emailPage) != 0 else None
        else:
            return

    def pdb(self):
        import pdb;pdb.set_trace()


class NewUserForm(GeneralMethod):
    label = _(u'Add New User')
    template = ViewPageTemplateFile('templates/new_user_form.pt')
    def __call__(self):
        request = self.request
        if request.form.get('widget-form-btn', '') == 'widget-form-btn':
            self.registerUser()
            return self.request.response.redirect(self.context.portal_url()+'/@@usergroup-userprefs')

        username = request.form.get('username', '')
        if username:
            return self.checkUsername()

        promoCode = request.form.get('promoCode', '')
        if promoCode:
            return self.checkPromoCode()

        return self.template()



class PersonalDetails(GeneralMethod):
    template = ViewPageTemplateFile('templates/personal_view.pt')
    def __call__(self):
        self.viewTitle = _(u'Personal Details')
        if not api.user.is_anonymous():
            formdata = self.request.form
            if formdata.get('widget-form-btn', '') == 'widget-form-btn':
                formNameList = ['fName'   , 'lName', 'email', 'telephone'  , 'fax'  , 'company', 'address1', 
                                'address2', 'city' , 'zip'  , 'country', 'state', 'newsletter', 'group']
                if self.checkAdmin():
                    formNameList.append('promoCode')
                self.setProperties(formNameList)

                current_url = self.request.URL
                if self.checkAdmin():
                    current_url = self.context.portal_url() + '/@@usergroup-userprefs'
                self.request.response.redirect(current_url)

            return self.template()
        else:
            portal_url = self.context.portal_url()
            self.request.response.redirect(portal_url+'/login')

    def checkAdmin(self):
        permissions = api.user.get_permissions().get('Manage Site', False)
        return permissions

    def getCurrentUser(self):
        if self.checkAdmin():
            username = self.request.get('userid', '')
            if username:
                user = api.user.get(username=username)
                if user:
                    return user
        return api.user.get_current()

    def setProperties(self, formNameList):
        request = self.request
        alsoProvides(request, IDisableCSRFProtection)
        mappingDict = {}
        portal_memberdata = getToolByName(self.context, "portal_memberdata")
        formdata = self.request.form
        for name in formNameList:
            if portal_memberdata.hasProperty(name) and formdata.has_key(name):
                mappingDict.update({name: formdata[name]})
            if name == 'newsletter' and formdata.has_key('newsletter'):
                self.updateEmailList(formdata['email'], formdata['newsletter'])
        self.getCurrentUser().setMemberProperties(mapping=mappingDict) 
        self.updateOtherLang(mappingDict)

    def updateEmailList(self, email, action):
        newsletter = self.getNewsletter()
        emailList = Set()
        if newsletter != None:
            emailList = newsletter.getObject().description.split('\r\n')
            emailList = Set([e for e in emailList if e != ''])
            if action == 'true':
                emailList.add(email)
            elif action == 'false':
                emailList.discard(email)
            request = self.request
            alsoProvides(request, IDisableCSRFProtection)
            emailStr = ''
            for email in emailList:
                emailStr += email + '\r\n'
            newsletter.getObject().description = emailStr

    def getNewsletter(self):
        portal = api.portal.get()
        if portal.hasObject('resource'):
            emailPage = api.content.find(portal['resource'], portal_type='Document', id='newsletter' )
            return emailPage[0] if len(emailPage) != 0 else None
        else:
            return
    
    def updateOtherLang(self, data):
        return
        request = self.request
        if 'alpha_cn' in request['URL']:
             requests_url = request['URL1'].replace('alpha_cn', 'alpha_en')
        else:
             requests_url = request['URL1'].replace('alpha_en', 'alpha_cn')
        user = self.getCurrentUser().id
        url = "{}/@users/{}".format(requests_url, user)
        response = requests.patch(url, headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                                  json= data,
                                  auth=('admin', '123456'))
        response = requests.post(request['URL1']+'/updateUserConfiglet', 
                                 headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                                 json= {'username': user, 'promoCode': data.get('promoCode', '')},
                                 auth=('admin', '123456'))
        response = requests.post(requests_url+'/updateUserConfiglet', 
                                 headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                                 json= {'username': user, 'promoCode': data.get('promoCode', '')},
                                 auth=('admin', '123456'))


class WishListView(GeneralMethod):
    @property
    def viewTitle(self):
        viewTitle = _(u'Wish List')
        return viewTitle

    def getUserProperty_wishList(self):
        user = api.user.get_current()
        if user:
            wishList = user.getProperty('wishList')
            if wishList:
                return wishList.split(', ')
            else:
                return []
        else:
            self.request.response.redirect(portal_url+'/login')

    def getWishList(self):
        wishUIDList = self.getUserProperty_wishList()
        wishList = []
        for uid in wishUIDList:
            item = api.content.get(UID=uid)
            if item:
                wishList.append(item)
        return wishList

class AddWishList(BrowserView):
    def setWishList(self, wishItemUID):
        user  = api.user.get_current()
        wishList = user.getProperty('wishList')
        checkUID = api.content.find(portal_type='Product', UID=wishItemUID)
        if len(checkUID) > 0:
            if wishList:
                if wishItemUID not in wishList:
                    wishList = wishList.split(', ')
                    wishList.append(wishItemUID)
                    wishList = ', '.join(wishList) 
                else:
                    msg = _(u'Add WishList Repeat!!')
                    trans_msg = api.portal.translate(msg, lang=self.context.Language())
                    return json.dumps({'error': trans_msg})
            else: 
                wishList = str(wishItemUID)
            alsoProvides(self.request, IDisableCSRFProtection)
            user.setMemberProperties(mapping={'wishList': wishList})

            msg = _(u'Add WishList Success!!')
            trans_msg = api.portal.translate(msg, lang=self.context.Language())
            return json.dumps({'success': trans_msg})
        else:
            msg = _(u'wishItemUID is not valid!!')
            trans_msg = api.portal.translate(msg, lang=self.context.Language())
            return json.dumps({'error': trans_msg})

    def __call__(self):
        query = self.request.form.copy()
        if not api.user.is_anonymous():
            if query.has_key('wishItemUID'):
                wishItemUID  = query['wishItemUID']
                return self.setWishList(wishItemUID)
            else:
                msg = _(u'Query string supplied is not valid')
                trans_msg = api.portal.translate(msg, lang=self.context.Language())
                return json.dumps({'error': trans_msg})
        else: 
            msg = _(u'Add WishList Must Be Login!!')
            trans_msg = api.portal.translate(msg, lang=self.context.Language())
            return json.dumps({'error': trans_msg})


class DelWishList(BrowserView):
    def delWishList(self, wishItemUID):
        user  = api.user.get_current()
        wishList = user.getProperty('wishList').split(', ')
        checkUID = api.content.find(portal_type='Product', UID=wishItemUID)
        if len(checkUID) > 0:
            if wishList:
                if wishItemUID in wishList:
                    wishList.remove(wishItemUID)
                    wishList = ', '.join(wishList) 
                    alsoProvides(self.request, IDisableCSRFProtection)
                    user.setMemberProperties(mapping={'wishList': wishList})

                    msg = _(u'Delete WishList Success!!')
                    trans_msg = api.portal.translate(msg, lang=self.context.Language())
                    return json.dumps({'success': trans_msg})

        msg = _(u'wishItemUID is not valid!!')
        trans_msg = api.portal.translate(msg, lang=self.context.Language())
        return json.dumps({'error': trans_msg})

    def __call__(self):
        query = self.request.form.copy()
        if not api.user.is_anonymous():
            if query.has_key('wishItemUID'):
                wishItemUID  = query['wishItemUID']
                return self.delWishList(wishItemUID)
            else:
                msg = _(u'Query string supplied is not valid')
                trans_msg = api.portal.translate(msg, lang=self.context.Language())
                return json.dumps({'error': trans_msg})
        else: 
            msg = _(u'Add WishList Must Be Login!!')
            trans_msg = api.portal.translate(msg, lang=self.context.Language())
            return json.dumps({'error': trans_msg})


class CheckPromoCode(BrowserView):
    def __call__(self):
        promoCode = getattr(self.request, 'promoCode', '')
        user = api.user.get_current().id
        existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode') or {}
        if str(promoCode) in existCode.values() and str(promoCode) != existCode.get(user, ''):
            return '1'
        else:
            return '0'

class UserAdd(BrowserView):
    def __call__(self):
        request  = self.request
        if request.get('BODY'):
            data = json.loads(self.request.get('BODY', '{}'))
            if data.has_key('username') and data.has_key('email') and data.has_key('password') and data.has_key('properties'):
                if not api.user.get(username=data['username']):
                    # Disable CSRF protection
                    alsoProvides(self.request, IDisableCSRFProtection)
                    try:
                        properties = data['properties']
                        user = api.user.create(username=data['username'], email=data['email'], password=data['password'], properties=properties)
                        return '{"success": "username":"user: '+ user.id +' is created"}'
                    except Exception as ex:
                        return '{"error": "username can not created"}'
                return '{"error": "username can not created"}'
            return '{"error": "Required username, email, password, fullname field is missing"}'
        return '{"error": "json data is missing"}'

class UserProperty(BrowserView):
    def __call__(self):
        request  = self.request
        propertyList = ['city', 'fax', 'group', 'zip', 'address2', 'address1', 'company', 'promoCode', 'telephone', 'lName', 'state', 'fName', 'country', 'fullname', 'newsletter', 'email']
        if request.get('BODY'):
            body = json.loads(self.request.get('BODY', '{}'))
            if body.has_key('username'):
                username = body['username']
                user = api.user.get(username=username)
                if user:
                    userProperty = {}
                    for p in propertyList:
                        userProperty.update({p : user.getProperty(p)})
                    data = json.dumps(userProperty)
                    return data
                return '{"error": "username is not exist"}'
            return '{"error": "Required username field is missing"}'
        return '{"error": "json data is missing"}'

class UpdateUserConfiglet(BrowserView):
    def __call__(self):
        request = self.request
        if request.get('BODY'):
            promoCode = json.loads(request.get('BODY')).get('promoCode', '')
            username = json.loads(request.get('BODY'))['username']
            if username:
                # Disable CSRF protection
                alsoProvides(self.request, IDisableCSRFProtection)

                existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode') or {}
                if promoCode:
                    existCode.update({str(username): str(promoCode)})
                else:
                    existCode.pop(str(username), '')
                api.portal.set_registry_record('alpha.content.browser.user_configlet.IUser.promoCode', existCode)
                return '{"success": "UserConfiglet is updated"}'
            return '{"error": "json data is missing"}'


class UseCouponStatus(BrowserView):
    template = ViewPageTemplateFile('templates/use_coupon_status.pt')
    def __call__(self):
        permissions = api.user.get_permissions().get('Manage Site', False)
        if permissions:
            request = self.request
            execSql = SqlObj()
            execStr = """SELECT * FROM coupon_status  ORDER BY `coupon_status`.`id` DESC"""
            self.data = execSql.execSql(execStr)

            return self.template()
        else:
            self.request.response.redirect(self.context.portal_url)

    @property
    def viewTitle(self):
        viewTitle = _(u'Order History')
        return viewTitle


class SqlSelect(BrowserView):
    def checkAdmin(self):
        permissions = api.user.get_permissions().get('Manage Site', False)
        return permissions

    @property
    def user(self):
        user = api.user.get_current()
        if self.checkAdmin():
            username = self.request.form.get('username', '')
            if username:
                user = api.user.get(username=username)
        return user

    @property
    def b_start(self):
        b_start = getattr(self.request, 'b_start', 0)
        return int(b_start)
    
    @property
    def b_size(self):
        b_size = getattr(self.request, 'b_size', 10)
        return int(b_size)

    @property
    def sort_on(self):
        sort_on = getattr(self.request, 'sort_on', 'sortable_title') 
        return sort_on

    @property
    def sort_order(self):
        sort_order = getattr(self.request, 'sort_order', 'ascending') 
        return sort_order
    
    @property
    def order_id(self):
        order_id = getattr(self.request, 'order_id', '')
        return order_id

    @property
    def start_date(self):
        start_date = getattr(self.request, 'start_date', '')
        return start_date

    @property
    def end_date(self):
        end_date = getattr(self.request, 'end_date', '')
        return end_date

    @property
    def sqlWhereStr(self):
        whereList = []
        if self.order_id:
            whereList.append("`order_id` LIKE '%%{}%%'".format(self.order_id))
        if self.start_date and self.end_date:
            whereList.append("(`date` BETWEEN '{}' AND '{}')".format(self.start_date, self.end_date))
        elif self.start_date:
            whereList.append("(`date` LIKE '%%{}%%')".format(self.start_date))
        return 'AND'.join(whereList)

    def batch(self):
        batch = Batch(
            self.results(),
            size=self.b_size,
            start=self.b_start,
            orphan=1
        )
        return batch


class OrderHistoryView(SqlSelect):
    @property
    def viewTitle(self):
        viewTitle = _(u'Order History')
        return viewTitle

    @property
    def sqlWhereStr(self):
        whereList = []
        if self.order_id:
            whereList.append("`order_id` LIKE '%%{}%%'".format(self.order_id))
        if self.start_date and self.end_date:
            whereList.append("(`time` BETWEEN '{}' AND '{}')".format(self.start_date, self.end_date))
        elif self.start_date:
            whereList.append("(`time` LIKE '%%{}%%')".format(self.start_date))
        return 'AND'.join(whereList)

    def checkAnonymous(self):
        if api.user.is_anonymous():
            self.request.response.redirect(self.context.portal_url())

    def getMyOrder(self):
        username = api.user.get_current().id
        execSql = SqlObj()
        execStr = "SELECT * FROM coupon_status WHERE `user` LIKE '{}' {} {} ORDER BY `time` DESC".format(username, ('AND' if self.sqlWhereStr else ''), self.sqlWhereStr)
        if self.checkAdmin():
            execStr = "SELECT * FROM coupon_status {} {} ORDER BY `time` DESC".format(('WHERE ' if self.sqlWhereStr else ''), self.sqlWhereStr)
        results = execSql.execSql(execStr)
        
	return results 

    def results(self):
        orderDict = defaultdict(list)
        for order in self.getMyOrder():
            orderDict[order['order_id']].append(order)
        orderList = []
        orderKeys = orderDict.keys()
        orderKeys.sort(reverse=True)
        for order_id in orderKeys:
            total_price = order['total']
            execSql = SqlObj()
            execStr = "SELECT * FROM bonus_history WHERE `order_id` = '{}' ORDER BY `date` DESC".format(order_id)
            items = execSql.execSql(execStr)
            orderList.append({'order_id':order_id, 'total_price':total_price, 'order_items': items, 'order': orderDict[order_id][0]})
        return orderList 


class BonusHistoryView(SqlSelect):
    template = ViewPageTemplateFile('templates/bonus_history_view.pt')
    def __call__(self):
        if api.user.is_anonymous():
            return

        request = self.request

        if self.checkAdmin():
            if self.request.get('widget-form-btn', '') == 'widget-admin-submit':
                self.changeBonusStatus()

        return self.template()

    @property
    def viewTitle(self):
        viewTitle = _(u'Bonus History')
        return viewTitle

    def getBonus(self):
        user = self.user
        execSql = SqlObj()
        execStr = "SELECT * FROM bonus_history WHERE `username` LIKE '{}' AND NOT `bonus_status` = 0 {} {} ORDER BY `date` DESC".format(user.getUserName(), ('AND' if self.sqlWhereStr else ''), self.sqlWhereStr)
        results = execSql.execSql(execStr)
        
	return results

    def results(self):
        orderDict = defaultdict(list)
        for bonus in self.getBonus():
            orderDict[bonus['order_id']].append(bonus)
        bonusList = []
        orderKeys = orderDict.keys()
        orderKeys.sort(reverse=True)
        for order_id in orderKeys:
            total_bonus = 0
            order_date = ''
            for item in orderDict[order_id]:
                total_bonus += item['all_bonus']
                order_date = item['date'].strftime('%Y-%m-%d')
            bonusList.append({'order_id':order_id, 'order_date': order_date, 'total_bonus':total_bonus, 'order_items': orderDict[order_id]})
        return bonusList 

    def changeBonusStatus(self):
        request = self.request
        id = request.form.get('id', '')
        qty = request.form.get('qty', '')
        username = self.user.getUserName()

        execSql = SqlObj()
        execStr = """SELECT * FROM bonus_history WHERE `id` LIKE '%s'""" % id
        results = execSql.execSql(execStr)
        status = results[0]['bonus_status']
        uni_bonus = results[0]['uni_bonus']
        all_bonus = results[0]['all_bonus']
        used_bonus = results[0]['used_bonus']
        qty = int(qty)
        b_qty = results[0]['qty']
        disc_bonus = qty * uni_bonus
        
        if status == 1:
            b_qty = b_qty - qty
            b_qty = b_qty if b_qty >= 0 else 0
            used_bonus = disc_bonus
            all_bonus = uni_bonus * b_qty
            if all_bonus == 0:
                status = 3

        execSql = SqlObj()
        execStr = "UPDATE bonus_history SET all_bonus = %s, used_bonus = %s, bonus_status = %s WHERE `id` = %s" \
                  %(all_bonus, used_bonus, status, int(id))
        results = execSql.execSql(execStr)

    def getStatusStr(self, status_code):
        statusStr = [_(u'usable'), _(u'unusable'), _(u'returned')]
        try:
            status = statusStr[status_code-1]
        except Exception:
            status = statusStr[1]
        return status


class RebateHistoryView(SqlSelect):
    template = ViewPageTemplateFile('templates/rebate_history_view.pt')
    def __call__(self):
        if api.user.is_anonymous():
            return
        request = self.request

        if self.checkAdmin():
            if self.request.get('widget-form-btn', '') == 'widget-admin-submit':
                self.changeRebateStatus()

        return self.template()

    @property
    def viewTitle(self):
        viewTitle = _(u'Rebate History')
        return viewTitle
    
    def getRebate(self):
        user = self.user
        execSql = SqlObj()
        execStr = "SELECT * FROM bonus_history WHERE `coupon_owner` LIKE '{}' AND NOT `rebate_status` = 0 AND `rebate` > 0 {} {} ORDER BY `date` DESC".format(user.getUserName(), ('AND' if self.sqlWhereStr else ''), self.sqlWhereStr)
        results = execSql.execSql(execStr)
        
	return results

    def results(self):
        rebate = self.getRebate() 
        orderDict = defaultdict(list)
        for rebate in self.getRebate():
            orderDict[rebate['order_id']].append(rebate)
        rebateList = []
        orderKeys = orderDict.keys()
        orderKeys.sort(reverse=True)
        for order_id in orderKeys:
            total_rebate = 0
            order_date = ''
            for item in orderDict[order_id]:
                total_rebate += (item['qty'] * item['rebate'])
                order_date = item['date'].strftime('%Y-%m-%d')
            rebateList.append({'order_id':order_id, 'order_date': order_date, 'total_rebate':total_rebate, 'order_items': orderDict[order_id]})
        return rebateList 

    def changeRebateStatus(self):
        request = self.request
        clearList = request.get('clear', [])
        returnList = request.get('return', [])
       
        for id in clearList: 
            execSql = SqlObj()
            execStr = "UPDATE bonus_history SET rebate_status = %s WHERE `id` = %s" \
                      %(2, int(id))
            results = execSql.execSql(execStr)

        for id in returnList: 
            execSql = SqlObj()
            execStr = "UPDATE bonus_history SET rebate_status = {0} , bonus_status = {0} WHERE `id` = {1}".format(3, int(id))
            results = execSql.execSql(execStr)

    def getStatusStr(self, status_code):
        statusStr = [_(u'unclear'), _(u'clear'), _(u'returned')]
        try:
            status = statusStr[status_code-1]
        except Exception:
            status = statusStr[0]
        return status
