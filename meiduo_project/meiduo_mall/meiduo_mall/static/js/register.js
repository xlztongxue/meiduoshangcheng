/**
 * Created by python on 19-9-23.
 */
let vm = new Vue({
    el:"#app", //通过ID选择器找到绑定页面的html页面
    delimiters:["[[","]]"],
    //获取数据对象
    data:{
        //v-model
        username:'',
        password:'',
        password2:'',
        mobile:'',
        allow:'',
        uuid:'',
        image_codes:'',
        image_codes_url:'',
        sms_code_tip:'获取短信验证码',

        //v-show
        error_name:false,
        error_password:false,
        error_password2:false,
        error_mobile:false,
        error_allow:false,
        error_image_codes:false,
        send_flag:false,
        error_sms_code:false,

        //error_message
        error_name_message:'',
        error_mobile_message:'',
        error_image_codes_message:'',
        error_sms_code_message:'',
    },
    //生成图形验证码
    mounted(){//页面加载完会被调用
        this.generate_image_code()
    },
    //定义和实现事件方法
    methods:{
        //　发送短信验证码
        send_sms_code(){
            //避免恶意用户频繁的点击获取短信验证码
            if(this.send_flag == true){
                return;
            }
            this.send_flag = true;
            //校验数据：mobile,image,image_code
            this.check_mobile();
            this.check_image_codes();
            if(this.error_mobile == true || this.error_image_codes == true){
                this.send_flag = false;
                return;
            }
            let url = '/sms_codes/' + this.mobile + '/?image_code=' + this.image_codes + '&uuid=' + this.uuid;
            axios.get(url,{
                responseType:'json'
            })
                .then(response => {
                    if(response.data.code=='0'){
                        // 验证码验证成功
                        //显示倒计时60秒效果
                        let num = 60;
                        let t = setInterval(()=>{
                             if(num == 1){//停止回调函数的执行
                                 clearInterval(t);//停止回调函数的执行
                                 this.sms_code_tip = '获取短信验证码';
                                 this.generate_image_code();//重新生成图形验证码
                                 this.send_flag = false;
                             } else {//正在倒计时
                                 num -= 1;
                                 this.sms_code_tip = num + '秒';
                             }
                        },1000)
                    } else if(response.data.code=='4001'){
                        //验证码验证不成功
                        this.error_image_codes_message = response.data.errmsg;
                        this.error_image_codes = true;
                        this.generate_image_code();
                        this.send_flag = false;
                    }else if (response.data.code == '4002') {
                        this.error_sms_code_message = response.data.errmsg;
                        this.error_sms_code = true;
                    }
                })
                .catch(error => {
                    console.log(error.response);
                    this.send_flag = false;

                })
        },
        // 生成图形验证码的方法：封装的思想，代码复用
        generate_image_code(){
            // 生成UUID，generateUUID() : 封装在common.js文件中，需要提前引入
            this.uuid = generateUUID();
            this.image_codes_url = '/image_codes/'+ this.uuid +'/';
        },
        //校验用户名
        //用户名是5-8个字符，[a-zA-Z0-9_-]
        check_username(){
            //^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z_]{5, 20}$
            let re = /(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z_-]{5,20}/;
            let re0 = /^$/;
            let re1 = /^[0-9a-zA-Z_-]{5,20}$/;
            let re2 = /^(?![0-9]+$)/;
            let re3 = /^(?![a-zA-Z]+$)/;
            //使用正则匹配用户数据
            if (re.test(this.username)){
                //匹配成功，不显示错误提示信息
                this.error_name = false;
            }else {
                //匹配不成功，显示错误提示信息
                if (re0.test(this.username)){
                    this.error_name_message = '用户名不能为空';
                }else if (!re1.test(this.username)){
                    this.error_name_message = '请输入5-20个字符的用户名';
                }else if (!re2.test(this.username)){
                    this.error_name_message = '用户名至少包含一个字母';
                }else if (!re3.test(this.username)){
                    this.error_name_message = '用户名至少包含一个数字';
                }else {
                     this.error_name_message = "用户名错误";
                }
                this.error_name = true;
            }
            //判断用户名是否重复注册
            //只有当用户输入的用户名满足条件才回去判断
            if (this.error_name == false){
                let url = '/usernames/'+ this.username +'/count/';
                axios.get(url, {
                    responseType:'json'
                })
                    .then(response =>{
                        if (response.data.count == 1){
                            //　用户名已存在
                            this.error_name_message = '用户名已存在';
                            this.error_name = true;
                        }else{
                            this.error_name = false;
                        }
                    })
                    .catch(error =>{
                        console.log(error.response)
                    })
            }
        },
        //校验密码
        check_password(){
            let re = /^[a-zA-Z0-9]{8,20}$/;
            //使用正则匹配用户数据
            if (re.test(this.password)){
                //匹配成功，不显示错误提示信息
                this.error_password = false;
            }else {
                //匹配不成功，显示错误提示信息
                this.error_password = true;
            }
        },
        //校验确认密码
        check_password2(){
            if (this.password2 == this.password){
                //匹配成功，不显示错误提示信息
                this.error_password2 = false;
            }else {
                //匹配不成功，显示错误提示信息
                this.error_password2 = true;
            }
        },
        //校验手机号
        check_mobile(){
            let re = /^1[3-9]\d{9}$/;
            //使用正则匹配用户数据
            if (re.test(this.mobile)){
                //匹配成功，不显示错误提示信息
                this.error_mobile = false;
            }else {
                //匹配不成功，显示错误提示信息
                this.error_mobile_message = '您输入的手机格式不正确';
                this.error_mobile = true;
            }
            //判断手机号是否重复注册
            //只有当用户输入的用户名满足条件才回去判断
            if (this.error_mobile == false){
                let url = '/mobiles/'+this.mobile +'/count/';
                axios.get(url, {
                    responseType:'json'
                })
                    .then(response =>{
                        if (response.data.count == 1){
                            //　手机号已存在
                            this.error_mobile_message = '手机号已存在';
                            this.error_mobile = true;
                        }else{
                            this.error_mobile = false;
                        }
                    })
                    .catch(error =>{
                        console.log(error.response)
                    })
            }
        },
        //　校验图形验证码
        check_image_codes(){
            if (this.image_codes.length != 4){
                this.error_image_codes_message = '请输入图形验证码';
                this.error_image_codes = true;
            }else {
                this.error_image_codes = false;
            }

        },
        check_sms_code(){
            if(this.sms_code.length != 6){
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },

        //校验是否勾选协议
        check_allow(){
            if(!this.allow){
                this.error_allow = true;
            }else {
                this.error_allow = false;
            }

        },

        //监听表单提交事件
        on_submit(){
            this.check_username();
            this.check_password();
            this.check_mobile();
            this.check_sms_code();
            this.check_allow();
            //在校验之后，注册数据中，只要有错误，就禁用掉表单的提交事件
            if (this.error_name == true||this.error_password == true ||this.error_password2||this.error_mobile == true ||this.error_allow == true
            ||this.error_image_codes == true||this.error_sms_code == true){
                window.event.returnValue = false;
            }
        },
    }
});