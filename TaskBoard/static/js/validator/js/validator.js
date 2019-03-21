$(function () {
    'use strict';

    window.Validator = function (val, rule) {

        this.is_valid = function (new_val) {
            let key;
            if (new_val !== undefined)
                val = new_val;
            if (!rule.required && !val)
                return true;

            for (key in rule) {
                if (key === 'required')
                    continue;
                let r = this['validate_' + key]();
                if (!r)
                    return false;
            }
            return true;
        }

        function pre_max_min() {
            val = parseFloat(val);
        }

        function pre_length() {
            val = val.toString();
        }

        this.validate_max = function () {
            pre_max_min();
            return val <= rule.max;
        }
        this.validate_min = function () {
            pre_max_min();
            return val >= rule.min;
        }
        this.validate_minlength = function () {
            pre_length();
            return val.length >= rule.minlength;
        }
        this.validate_maxlength = function () {
            pre_length();
            return val.length <= rule.maxlength;
        }
        this.validate_numeric = function () {
            return $.isNumeric(val);
        }
        this.validate_pattern = function () {
            let reg = new RegExp(rule.pattern);
            return reg.test(val);
        }
        this.validate_required = function () {
            let real = $.trim(val);
            if (!real && real !== 0)
                return false;
            return true;
        }
    }
})
