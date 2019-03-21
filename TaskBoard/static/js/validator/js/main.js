$(function () {
    'use strict';

    let $inputs = $('[data-rule]'),
        $form = $('#signup'),
        inputs = [];
    $inputs.each(function (index, node) {
        let tmp = new Input(node);
        inputs.push(tmp);
    })
    $form.on('submit', function (e) {
        e.preventDefault();
        $inputs.trigger('blur');

        for (let i = 0; i < inputs.length; i++) {
            let item = inputs[i];
            let r = item.validator.is_valid();
            if (!r) {
                alert('invalid');
                return;
            }
        }
        alert('success');
        signup();
    })

    function signup() {
        // 
        alert('post')
    }
})
