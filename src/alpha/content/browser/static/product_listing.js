var product = {
    template:
    `<div class="single-product mb-30">
          <div class="single-img">
            <a v-bind:href="url">
              <img v-bind:src="image"  class="first" style="width:262px;height:262px"/>
            </a>
          </div>
          <div class="product-content">
            <span>{{product_number}}</span>
            <h3><a v-bind:href="url">{{title}}</a></h3>
            <div class="product-price">
              <ul>
		<template v-if="sale_price == null">
                  <li class="new-price" >{{price}}</li>
		</template>
		<template v-else>
                  <li class="new-price sale"> {{sale_price}}</li>
                  <li class="old-price">{{price}}</li>
		</template>
              </ul>
            </div>
            <div class="add-to-links mt-15">
              <ul>
                <li><a class="add_shop" v-bind:data-title="title" v-bind:data-price="price" v-bind:data-uid="uid"
			v-bind:data-sale_price="sale_price" v-bind:data-url="url" v-bind:data-image="image" >
			<i class="fa fa-shopping-cart"></i></a></li>
                <li><a href="#"><i class="fa fa-refresh"></i></a></li>
                <li><a href="#"><i class="fa fa-heart-o"></i></a></li>
                <li><a href="#" data-toggle="modal" data-target="#mymodal"><i class="fa fa-eye"></i></a></li>
              </ul>
            </div>
          </div>
      </div>`,
    props: ['title','product_number','price', 'sale_price', 'url', 'image', 'uid']
}

Vue.component('paginate', VuejsPaginate)
var product_listing = new Vue({
    el: '#product-listing',
    data: {
        product_data: [],
	none_limit_data: [],
	origin_data: [],
        pages: 0,
        now_page: 0,
	numbers: 12,
	sort: 'a-z',
    },
    created: function(){
try{
	this.origin_data = JSON.parse(document.getElementById('productData').innerText)
	origin_data = this.origin_data
	product_data = this.product_data
	this.none_limit_data = origin_data
	numbers = this.numbers
	count = 0
	while (product_data.length < numbers){
	    if(product_data.length == this.none_limit_data.length){
		break
	    }else{
	        product_data.push(origin_data[count])
	        count ++
	    }
	}
	total_number = origin_data.length
	if (total_number % numbers != 0){
	    this.pages = Math.floor(total_number / numbers) +1
	}
	else{
	    this.pages = total_number / numbers
	}
}
catch(err){
debugger
}
    },
    components:{
        'product': product,
    },
    methods: {
        add: function(item_id){
        },
        change_page: function(page){
	    product_data = this.product_data
	    none_limit_data = this.none_limit_data
	    numbers = this.numbers
	    start = (page - 1) * numbers
	    this.product_data = []
	    while(this.product_data.length < numbers){
                if(start == this.none_limit_data.length){
                    break
                }else{
	            this.product_data.push(this.none_limit_data[start])
		    start ++
                }
	    }
        },
	change_numbers: function(){
            numbers = this.numbers
	    count = 1
            start = 0
            this.product_data = []
            while(this.product_data.length < numbers){
                this.product_data.push(this.none_limit_data[start])
                start ++
            }
	    total_number = this.none_limit_data.length
            if (total_number % numbers != 0){
                this.pages = Math.floor(total_number / numbers) +1
            }
            else{
                this.pages = total_number / numbers
            }
	},
	change_sort: function(){
            sort = this.sort
            origin_data = this.origin_data
            if(sort == 'highest'){
                origin_data.sort(function(a,b){
                    a_price = product_listing.judge_price(a)
                    b_price = product_listing.judge_price(b)
                    return b_price - a_price
                })
            }else if(sort == 'lowest'){
                origin_data.sort(function(a,b){
                    a_price = product_listing.judge_price(a)
                    b_price = product_listing.judge_price(b)
                    return a_price - b_price
                })
            }else if(sort == 'a-z'){
                origin_data.sort(function(a,b){
                    a_title = a[0].toUpperCase()
                    b_title = b[0].toUpperCase()
                    if(a_title > b_title){
                        return 1
                    }
                    if(a_title < b_title){
                        return -1
                    }
                    return 0
                })
            }else if(sort == 'z-a'){
                origin_data.sort(function(a,b){
                    a_title = a[0].toUpperCase()
                    b_title = b[0].toUpperCase()
                    if(a_title > b_title){ 
                        return -1
                    }
                    if(a_title < b_title){ 
                        return 1
                    }
                    return 0

                })
            }
            activity = $('.activity')
            if(activity.length == 0){
		product_listing.no_activity()
            }else{
                mode = activity.data('mode')
                if(mode == 'brand'){
                    brand = activity.data('brand')
                    product_listing.change_brand(brand)
                }else if(mode == 'category'){
                    category = activity.data('category')
                    subject = activity.data('subject')
                    product_listing.change_category(category, subject)
                }
            }
	},
        judge_price: function(product){
            if(product[1][4]){
                return parseInt(product[1][4])
            }else{
                return parseInt(product[1][3])
            }
        },
	change_category: function(category, subject){
	   origin_data = this.origin_data
	    numbers = this.numbers
	    count  = 1
	    none_limit_count = 1

            this.none_limit_data = []
            low = parseInt($('#amount1').val().split('-')[0].trim())
            height = parseInt($('#amount1').val().split('-')[1].trim())
	    this.product_data = origin_data.filter(function(value){
		price = product_listing.judge_price(value)

		if(value[1][0] == category && value[1][1] == subject && price >= low && price <= height){
		    none_limit_count ++
		    product_listing.none_limit_data.push(value)
		    if(count <= numbers){
		         count ++
		         return value
		    }
		}
	    })
            if (none_limit_count % numbers != 0){
                this.pages = Math.floor(none_limit_count / numbers) +1
            }
            else{
                this.pages = none_limit_count / numbers
            }
	},
	change_brand: function(brand){
            origin_data = this.origin_data
            numbers = this.numbers
	    count = 1
	    none_limit_count = 1
            this.none_limit_data = []
            low = parseInt($('#amount1').val().split('-')[0].trim())
            height = parseInt($('#amount1').val().split('-')[1].trim())
            this.product_data = origin_data.filter(function(value){
		price = product_listing.judge_price(value)
		if(value[1][2] == brand && price >= low && price <= height){
		    none_limit_count ++
                    product_listing.none_limit_data.push(value)
	            if(count <= numbers){
                        count ++
                        return value
		    }
		}
            })
            if (none_limit_count % numbers != 0){
                this.pages = Math.floor(none_limit_count / numbers) +1
            }
            else{
                this.pages = none_limit_count / numbers
            }
	    $('.page_list:nth-child(2)').addClass('active')
	},
        change_price_range: function(low, height){
            this.none_limit_data = []
            this.product_data = []
            product_data = this.product_data
            numbers = this.numbers
            none_limit_count = 1
	    activity = $('.activity')
	    mode = activity.data('mode')
	    if(activity.length == 0){
		product_listing.no_activity()
	    }
            else if(mode == 'brand'){
                brand = activity.data('brand')
                product_listing.change_brand(brand)
            }else if(mode == 'category'){
                category = activity.data('category')
                subject = activity.data('subject')
                product_listing.change_category(category, subject)
            }
        },
	no_activity: function(){
            origin_data = this.origin_data
            numbers = this.numbers
            count = 1
            none_limit_count = 1
            this.none_limit_data = []
            low = parseInt($('#amount1').val().split('-')[0].trim())
            height = parseInt($('#amount1').val().split('-')[1].trim())
	    this.product_data = this.origin_data.filter(function(value){
   	        price = product_listing.judge_price(value)
		if(price >= low || price <= height){
		    product_listing.none_limit_data.push(value)
		    none_limit_count ++
		    if(count <= numbers){
			count ++
			return value
		    }
		}
	    })
            if (none_limit_count % numbers != 0){
                this.pages = Math.floor(none_limit_count / numbers) +1
            }
            else{
                this.pages = none_limit_count / numbers
            }
            $('.page_list:nth-child(2)').addClass('active')
	}
    }
});


