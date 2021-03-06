function Register_password_validator() {
    let form = $('#change_password_form');
    form.find('[data-rule]').each(function () {
        new Input($(this));
    });
    let password1 = $('#password1');
    let password2 = $('#password2');
    let error = password2.next('div.input-error');
    password1.on('blur', function () {
        password2.trigger('blur');
    });
    password2.on('blur', function () {
        if (password1.val() === password2.val()) {
            error.hide();
        } else {
            error.show();
        }
    });
}

function Edit_Tag() {
    let select_option = $('#Tags_Edit option:selected');
    let tag_val = select_option.val();
    if (tag_val === '-2') {
        Add_Tag();
        return;
    }
    let tag_name = select_option.text();
    layer.open({
        type: 1,
        skin: "demo-class",
        area: ['400px', '200px'],
        title: 'Edit Tag',
        content: `<div class="text-center" style="margin-top:20px"><label for="tag_edit_input" class="form-group">Tag name:</label><input class="form-control" id="tag_edit_input" value="${tag_name}"></div>`,
        btn: ['修改', '删除', '取消'],
        anim: 1,
        offset: '150px',
        yes: function (index) {
            let tag_input = $('#tag_edit_input');
            tag_input.change(function () {
                tag_input.css('border', '1px solid #dbdbdb');
            });
            let tag = tag_input.val();
            if (tag === '') {
                tag_input.css('border', '1px solid #ff0000');
                tag_input.focus().select();
                layer.msg('Please input a name !');
                return;
            }
            $.ajax({
                url: "{{ url_for('setting.edit_tag') }}",
                type: 'POST',
                data: {
                    'tag_id': tag_val,
                    'tag': tag
                },
                success: function (e) {
                    if (e === 'ok') {
                        layer.close(index);
                        layer.msg('修改成功！');
                        socket.emit('refresh');
                        setTimeout(() => {
                            parent.location.reload();
                        }, 700);
                    } else if (e === 'same') {
                        let msg = 'The tag name you input almost existed, please re-entry !';
                        layer_error_msg(tag_input, msg);
                        return;
                    } else {
                        layer.msg('修改失败！')
                    }
                },
            });
        },
        btn2: function (index) {
            $.ajax({
                url: "{{ url_for('setting.delete_tag') }}",
                type: 'POST',
                data: {
                    'tag_id': tag_val,
                },
                success: function (e) {
                    if (e === 'ok') {
                        layer.close(index);
                        layer.msg('删除成功！');
                        socket.emit('refresh');
                        setTimeout(() => {
                            parent.location.reload();
                        }, 700);
                    } else {
                        layer.msg('删除失败！')
                    }
                },
            });
            return;
        },
        btn3: function (index) {
            layer.close(index);
        }
    });

}

function Add_Tag() {
    layer.open({
        type: 1,
        skin: "layui-layer-rim",
        area: ['400px', '200px'],
        title: 'Add Tag',
        content: '<div class="text-center" style="margin-top:20px"><label for="tag_add_input" class="form-group">Tag name:</label><input class="form-control" id="tag_add_input"></div>',
        btn: ['确定', '取消'],
        anim: 1,
        offset: '150px',
        yes: function (index) {
            let tag_input = $('#tag_add_input');
            tag_input.change(function () {
                tag_input.css('border', '1px solid #dbdbdb');
            })
            let tag = tag_input.val();
            if (tag === '') {
                tag_input.css('border', '1px solid #ff0000');
                tag_input.focus().select();
                layer.msg('Please input a name !');
                return;
            }
            $.ajax({
                url: "{{ url_for('setting.add_tag') }}",
                type: 'POST',
                data: {
                    'tag': tag
                },
                success: function (e) {
                    if (e === 'ok') {
                        layer.close(index);
                        layer.msg('添加成功！');
                        socket.emit('refresh');
                        setTimeout(() => {
                            parent.location.reload();
                        }, 700);
                    } else if (e === 'same') {
                        let msg = 'The tag name you input almost existed, please re-entry !';
                        layer_error_msg(tag_input, msg);
                        return;
                    } else {
                        layer.msg('添加失败！')
                    }
                },
            });
        },
        btn2: function (index) {
            layer.close(index);
        }
    });
}

function Register_email_validator() {
    new Input($('#email'));
}

function Register_username_validator() {
    new Input($('#username'));
}

function Register_status_change() {
    let ele = $(this);
    let project_id = ele.val();
    let project_title = $('#project_title' + project_id).text();
    $.ajax({
        url: "{{ url_for('setting.change_project_status') }}",
        type: 'POST',
        data: {
            'project_id': project_id,
        },
        success: function (e) {
            if (e === 'ok') {
                socket.emit('refresh');
                layer.msg(project_title + '状态修改成功。');
                let tr_ele = ele.parents('tr');
                if (tr_ele.attr('data-status') === 'False') {
                    tr_ele.attr('data-status', 'True');
                } else if (tr_ele.attr('data-status') !== 'True') {
                    return;
                }
                tr_ele.attr('data-status', 'False');
            } else {
                layer.msg(project_title + '状态修改失败！');
            }
        },
        error: function (error) {
            console.log(error);
        },
    });
}

function UserAndStatusFilter() {
    $('label[name="status"] input').change(Register_status_change);
    let user_filter_val = $('#show_by_user option:selected').val();
    let status_filter_val = $('#filter_by_status option:selected').val();
    let active_tr = $('tr[data-status="True"]');
    let inactive_tr = $('tr[data-status="False"]');
    if (user_filter_val !== 'any') {
        $('ul[name="users"]>li[name!=' + user_filter_val + ']').parents('tr').hide();
        $('ul[name="users"]>li[name=' + user_filter_val + ']').parents('tr').show();
    } else {
        $('ul[name="users"]').parents('tr').show();
    }
    if (status_filter_val === 'all') {
        active_tr.each(function () {
            if ($(this).is(':hidden'))
                return
            $(this).show();
        });
        inactive_tr.each(function () {
            if ($(this).is(':hidden'))
                return;
            $(this).show();
        });
    } else if (status_filter_val === 'active') {
        inactive_tr.hide();
    } else if (status_filter_val === 'inactive') {
        active_tr.hide();
    }
}

function del_user(the, user_id) {
    let name = $(the).parents('tr').children('td').eq(0).text();
    layer.open({
        type: 1,
        skin: "layui-layer-rim",
        area: ['400px', '200px'],
        title: '删除用户',
        content: '<div class="text-center" style="margin-top:20px"><p>是否确定删除用户 <span class="label label-danger">' +
            name + '</span> ?</p></div>',
        btn: ['删除', '取消'],
        anim: 6,
        offset: '150px',
        yes: function (index) {
            $.ajax({
                url: "{{ url_for('setting.del_user_by_id') }}",
                type: 'POST',
                data: {
                    'user_id': user_id,
                },
                success: function (e) {
                    if (e === 'ok') {
                        layer.close(index);
                        layer.msg('删除成功！');
                        socket.emit('refresh');
                        setTimeout(() => {
                            parent.location.reload();
                        }, 700);
                    } else {
                        layer.msg('删除失败！')
                    }
                },
            });
        },
        btn2: function (index) {
            layer.close(index);
        }
    });
}

function del_project(the, project_id) {
    let title = $(the).parents('tr').children('td').eq(0).text();
    layer.open({
        type: 1,
        skin: "layui-layer-rim",
        area: ['400px', '200px'],
        title: '删除用户',
        content: '<div class="text-center" style="margin-top:20px"><p>是否确定删除项目 <span class="label label-danger">' +
            title + '</span> ?</p></div>',
        btn: ['删除', '取消'],
        anim: 6,
        offset: '150px',
        yes: function (index, layero) {
            $.ajax({
                url: "{{ url_for('setting.del_project_by_id') }}",
                type: 'POST',
                data: {
                    'project_id': project_id,
                },
                success: function (e) {
                    if (e === 'ok') {
                        socket.emit('refresh');
                        layer.close(index);
                        layer.msg('删除成功！');
                        setTimeout(() => {
                            parent.location.reload();
                        }, 700);
                    } else {
                        layer.msg('删除失败！')
                    }
                },
            });
        },
        btn2: function (index) {
            layer.close(index);
        }
    });
}

function show_user_edit_modal(user_id) {
    let form = $('#UserEditModalForm' + user_id);
    form.find('[data-rule]').each(function () {
        new Input($(this));
    });
    let password1 = $('#user_password1_input' + user_id);
    let password2 = $('#user_password2_input' + user_id);
    let error = password2.next('div.input-error');
    password1.on('blur', function () {
        password2.trigger('blur');
    });
    password2.on('blur', function () {
        if (password1.val() === '' && password2 === '' || password1.val() === password2.val()) {
            error.hide();
        } else {
            error.show();
        }
    });
    $('#EditUserModal' + user_id).modal('show');
}

function show_user_add_modal() {
    let form = $('#UserEditModalForm');
    form.find('[data-rule]').each(function () {
        new Input($(this));
    });
    let password1 = $('#add_user_password1_input');
    let password2 = $('#add_user_password2_input');
    let error = $('#password2-error');
    password1.on('blur', function () {
        password2.trigger('blur');
    });
    password2.on('blur', function () {
        if (password1.val() === password2.val()) {
            error.hide();
        } else {
            error.show();
        }
    });
    $('#AddUserModal').modal('show');
}

function user_modal_save(user_id) {
    let form = $("#UserEditModalForm" + user_id);
    let password1_input = $('#user_password1_input' + user_id);
    let password2_input = $('#user_password2_input' + user_id);
    if (user_id !== '' && password1_input.val() === '' && password2_input.val() === '')
        password1_input.removeAttr('data-rule');
    let $inputs = form.find('[data-rule]');
    let inputs_array = [];
    $inputs.each(function () {
        inputs_array.push(new Input($(this)));
    });
    $inputs.trigger('change');
    password2_input.trigger('blur');
    let password2_input_error = password2_input.next('div:visible');
    if (password2_input_error.length !== 0) {
        layer.msg('Please check out your input carefully !');
        return;
    }
    for (let i = 0; i < inputs_array.length; i++) {
        let item = inputs_array[i];
        let r = item.validator.is_valid();
        if (!r) {
            layer.msg('Please check out your input carefully !');
            return;
        }
    }
    let modal = $('#EditUserModal' + user_id);
    $.ajax({
        url: "{{ url_for('setting.save_user_edit_modal') }}",
        type: 'POST',
        data: form.serialize(),
        success: function (status) {
            if (status !== 'fail') {
                if (status === 'same username') {
                    let username_input = $('#user_username_input' + user_id);
                    let msg = 'You input the username already exists, please re-entry !';
                    layer_error_msg(username_input, msg);
                    return;
                }
                if (status === 'same email') {
                    let email_input = $('#user_email_input' + user_id);
                    let msg = 'You input the email adress already exists, please re-entry !';
                    layer_error_msg(email_input, msg);
                    return;
                }
                modal.modal('hide');
                if (status === 'edit')
                    layer.msg('修改成功！');
                else if (status === 'add')
                    layer.msg('添加成功！');
                socket.emit('refresh');
                setTimeout(() => {
                    parent.location.reload();
                }, 300);
            } else {
                layer.msg('修改失败！')
            }
        },
        error: function (error) {
            console.log(error);
        },
    });
}

function is_valid(ele, msg) {
    if (ele.val() === '') {
        layer_error_msg(ele, msg);
        return false;
    }
    return true;
}

function is_valid_array(inputs_array) {
    for (let i = 0; i < inputs_array.length; i++) {
        let item = inputs_array[i];
        let r = item.validator.is_valid();
        if (!r) {
            layer.msg('Please check out your input carefully !');
            return false;
        }
    }
    return true;
}

function change_user_password() {
    let current_password = $('#password');
    let password1_input = $('#password1');
    let password2_input = $('#password2');
    let form = $('#change_password_form');
    let $inputs = form.find('[data-rule]');
    let inputs_array = [];
    $inputs.each(function () {
        inputs_array.push(new Input($(this)));
    });
    $inputs.trigger('change');
    password2_input.trigger('blur');
    if (!is_valid(current_password, 'Please input current password !')) return;
    if (!is_valid(password1_input, 'Please input new password !')) return;
    if (!is_valid(password2_input, 'Please input password again !')) return;
    if (!is_valid_array(inputs_array)) return;
    $.ajax({
        url: "{{ url_for('setting.change_user_password') }}",
        type: 'POST',
        data: {
            'current_password': current_password.val(),
            'password': password1_input.val()
        },
        success: function (status) {
            if (status !== 'fail') {
                if (status === 'ok') {
                    socket.emit('refresh');
                    layer.msg('Password reset complete！');
                    $('#change_password_form').find('input').val('');
                } else if (status === 'invalid') {
                    let ele = $('#password');
                    let msg = 'Current password is invalid, Please input again！';
                    layer_error_msg(ele, msg);
                }
            } else {
                layer.msg('Password change unsuccessful, Please try again later！')
            }
        },
        error: function (error) {
            console.log(error);
        },
    });

}

function change_user_username_or_email(name) {
    let info_input = $('#' + name);
    let input_validator = new Input(info_input);
    if (!input_validator.validator.is_valid()) {
        let ele = info_input;
        let msg = name + ' format is not correct !';
        layer_error_msg(ele, msg);
        return;
    }
    $.ajax({
        url: "{{ url_for('setting.change_user_username_or_email') }}",
        type: 'POST',
        data: {
            'name': name,
            'info': info_input.val(),
        },
        success: function (status) {
            if (status !== 'fail') {
                if (status === 'ok') {
                    layer.msg(name + ' change success！', {
                        end: function () {
                            if (name === 'email') {
                                $('#users_table_div').load('{{ url_for("setting.ajax_load_user_table") }}');
                                $('#email').val('');
                            } else if (name === 'username')
                                parent.location.reload();
                            socket.emit('refresh');
                        }
                    });
                } else if (status === 'same') {
                    let msg = 'You input the ' + name + ' already exists, please re-entry !';
                    let ele = info_input;
                    layer_error_msg(ele, msg);
                }
            } else {
                layer.msg(name + ' change unsuccessful, please try again later！')
            }
        },
        error: function (error) {
            console.log(error);
        },
    });
}