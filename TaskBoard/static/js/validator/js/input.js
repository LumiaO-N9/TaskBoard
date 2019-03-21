$(function () {
    'use strict';

    window.Input = function (selector) {
        let $ele, $error_ele, me = this,
            rule = {
                required: true
            };
        this.load_validator = function () {
            let val = this.get_val();
            this.validator = new Validator(val, rule);
        }

        this.get_val = function () {
            return $ele.val();
        }

        this.get_name = function () {
            return $ele.attr('name');
        }

        function init() {
            find_ele();
            get_error_ele();
            parse_rule();
            me.load_validator();
            listen();
        }

        function find_ele() {
            if (selector instanceof jQuery) {
                $ele = selector;
            } else {
                $ele = $(selector);
            }
        }

        function get_error_ele() {
            // $error_ele = $(get_error_selector());
            $error_ele = $ele.next('div.input-error');
        }

        // function get_error_selector() {
        //     return ;
        // }

        function parse_rule() {
            let rule_str = $ele.data('rule');
            if (!rule_str)
                return;
            let rule_arr = rule_str.split('|');
            for (let i = 0; i < rule_arr.length; i++) {
                let item_str = rule_arr[i];
                let item_arr = item_str.split(':');
                rule[item_arr[0]] = JSON.parse(item_arr[1]);
            }
        }

        function listen() {
            $ele.on('change', function () {
                let valid = me.validator.is_valid(me.get_val());
                if (valid)
                    $error_ele.hide();
                else
                    $error_ele.show();
            })
        }

        init();
    }
})
