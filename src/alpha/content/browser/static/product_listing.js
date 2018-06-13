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
                <li><a href="#"><i class="fa fa-shopping-cart"></i></a></li>
                <li><a href="#"><i class="fa fa-refresh"></i></a></li>
                <li><a href="#"><i class="fa fa-heart-o"></i></a></li>
                <li><a href="#" data-toggle="modal" data-target="#mymodal"><i class="fa fa-eye"></i></a></li>
              </ul>
            </div>
          </div>
      </div>`,
    props: ['title','product_number','price', 'sale_price', 'url', 'image']
}

Vue.component('paginate', VuejsPaginate)
var product_listing = new Vue({
    el: '#product-listing',
    data: {
        product_data: [],
	origin_data: [],
        pages: 0,
        now_page: 0,
	numbers: 12,
	sort: 'a-z'
    },
    created: function(){
	this.origin_data = JSON.parse(document.getElementById('productData').innerText)
	origin_data = this.origin_data
	product_data = this.product_data
	count = 0
	while (product_data.length < 9){
	    product_data.push(origin_data[count])
	    count ++
	}
	total_number = origin_data.length
	if (total_number % 9 != 0){
	    this.pages = Math.floor(total_number / 9) +1
	}
	else{
	    this.pages = total_number / 9
	}
    },
    components:{
        'product': product,
    },
    methods: {
        add: function(item_id){
        },
        change_page: function(page){
	    this.product_data = []
	    product_data = this.product_data
	    origin_data = this.origin_data
	    numbers = this.numbers
	    count = (page - 1) * 9
	    debugger
	    while(product_data.length < numbers){
		if(count >= origin_data.length){
		    break
		}else{
		    product_data.push(origin_data[count])
		    count ++
		}
	    }
        },
        prev_page: function(){
            if(this.now_page != 1){
                prev_page = this.now_page - 1
                this.change_page(prev_page)
            }else{
                return 
            }
        },
        next_page: function(){
            next_page = this.now_page + 1
            len = this.pages.length
            if(next_page <= this.pages[len-1]){
                this.change_page(next_page)
            }else{
                return 
            }
        },
	change_numbers: function(){

	},
	change_sort: function(){

	},
	change_category: function(category, subject){
	    origin_data = this.origin_data
	    numbers = this.numbers
	    this.product_data = origin_data.filter(function(value){
		return value[1][0] == category && value[1][1] == subject
	    })

            total_number = this.product_data.length
            if (total_number % 9 != 0){
                this.pages = Math.floor(total_number / 9) +1
            }
            else{
                this.pages = total_number / 9
            }
	}
    }

});


