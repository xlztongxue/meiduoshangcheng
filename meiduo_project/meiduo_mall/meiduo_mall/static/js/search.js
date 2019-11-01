let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        sku_count: 1,
    },
    mounted(){
    },
    methods: {
        // 加入购物车
        add_carts(sku_id){
            let url = '/carts/';
            axios.post(url, {
                sku_id: parseInt(sku_id),
                count: this.sku_count
            }, {
                headers: {
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType: 'json',
                withCredentials: true
            })
                .then(response => {
                    if (response.data.code == '0') {
                        alert('添加购物车成功');
                        this.cart_total_count += this.sku_count;
                    } else { // 参数错误
                        alert(response.data.errmsg);
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
    }
});