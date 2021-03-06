function EnterPress(event) {
    let input = $(this);
    if (event.keyCode === 13) {
        input.trigger('blur');
    }
}

function layer_error_msg(ele, msg) {
    layer.msg(msg, {
        skin: 'layer-error-skin',
        time: 2000,
        offset: '100px',
        end: function () {
            ele.css('border', '1px solid #ff0000');
            ele.focus().select();
            ele.on('change', function () {
                ele.css('border', '1px solid #dbdbdb');
            });
        }
    });
}

function check_if_same(ul, input, name) {
    let title_array = [];
    let id_array = [];
    let last_li_id = '1';
    ul.find('span[name=' + name + '_title_span]:visible').each(function () {
        title_array.push($(this).text());
        id_array.push($(this)[0].id.split(name + '_span')[1]);
    });
    let title = input.val();
    if (title.trim() === '') {
        return false;
    }
    if (title_array.indexOf(title.trim()) > -1) {
        let msg = 'This Project is already has the same name ' + name + ', Please check another one !';
        let ele = input;
        layer_error_msg(ele, msg);
        return false;
    }
    while (id_array.indexOf(last_li_id) > -1) {   // 解决id冲突
        last_li_id = (parseInt(last_li_id) + 1).toString();
    }
    return last_li_id;
}

function Register_color_picker(project_id) {
    $('#color_picker' + project_id).each(function () {
        let ele = $(this);
        ele.attr('data-color', '#D9EDF7');
        layui.use('colorpicker', function () {
            let colorpicker = layui.colorpicker;
            //渲染
            colorpicker.render({
                elem: ele,  //绑定元素
                color: '#D9EDF7', //设置默认色
                size: 'lg',
                predefine: true,
                colors: ['#dff0d8', '#d9edf7', '#fcf8e3', '#f2dede', '#337ab7'],
                change: function (color) {
                    ele.attr('data-color', color);
                }
            });
        });
    });
}

function edit_milestone_or_category_title(the) {
    $(the).hide();
    $(the).parents('li').children('span[name=old_title]').next().hide().next().show().focus();
}

function save_milestone_or_category_title_change(the, name) {
    let input = $(the);
    let ul = input.parents('ul').eq(0);
    if (check_if_same(ul, input, name)) {
        let span = input.prev();
        let a = input.next('div').children('a');
        span.text(input.val());
        span.show();
        a.show();
        input.hide();
    } else {
        return;
    }
}

function hide_milestone_or_category(the) {
    $(the).parents('li').hide();
}

function add_milestone_or_category(project_id, name) {
    let ul = $('#' + name + '_ul' + project_id);
    let input = $('#' + name + 'NameInput' + project_id)
    input.css('border', '1px solid #dbdbdb');
    let last_li_id = check_if_same(ul, input, name);
    let title = input.val();
    if (last_li_id) {
        input.val('');
    } else
        return;
    let instance = {
        id: last_li_id,
        title: title
    };
    let li_str = '';
    let color = '';
    if (name === 'milestone') {
        li_str = `<li name ="temporary" id="milestone_li${instance.id}" class="list-group-item" value="${instance.id}">
                <span class="fa fa-arrows-v pull-left" style="margin-left: -15px;padding-left: 10px">  |</span>`;
    } else if (name === 'category') {
        color = $('#color_picker' + project_id).attr('data-color');
        li_str = `<li name ="temporary" id="category_li${instance.id}" class="list-group-item" value="${instance.id}" style="text-transform: capitalize;background:${color}">`;
    }
    ul.append(li_str + `
                 <span name="old_title" hidden>${instance.title}</span>
                <span name="${name}_title_span" id="${name}_span${instance.id}"  style="width: 170px;display: inline-block;word-wrap:break-word;">${instance.title}</span>
                <input name="${name}_input" onblur="save_milestone_or_category_title_change(this,'${name}')"
                       onfocus="this.select()" class=""
                       id="${name}_input${instance.id}"
                       value="${instance.title}"
                       style="width: auto;border-radius:4px;border:1px solid #DBDBDB;"
                       hidden>
                <div class="pull-right">
                    <a id="${name}_a${instance.id}" name="edit"
                       onclick="edit_milestone_or_category_title(this)">
                        <span class="glyphicon glyphicon-edit"></span>
                    </a>
                    <a name="hide" onclick="hide_milestone_or_category(this)">
                        <span class="glyphicon glyphicon-trash" style="margin-left:4px"></span>
                    </a>
                </div>
            </li>`
    );
    $('input[name=' + name + '_input]').bind('keypress', EnterPress);
}

function show_project_edit_modal(project_id) {
    let input = $('#project_title_input' + project_id);
    input.css('border', '1px solid #DBDBDB');
    input.next().hide();
    let milestone_ul = $('#milestone_ul' + project_id);
    let category_ul = $('#category_ul' + project_id);
    let color_picker = $('#color_picker' + project_id);
    let select_users = $('#select_users' + project_id);
    milestone_ul.children('li[name=temporary]').remove();
    category_ul.children('li[name=temporary]').remove();
    milestone_ul.next('input').val('');
    category_ul.next('input').val('');
    $('span[name=old_title]').each(function () {
        let old_ele = $(this);
        old_ele.next('span').text(old_ele.text());
        old_ele.next('input').val(old_ele.text());
    });
    input.val(input.prev('span').text());
    let $input = new Input(input);
    input.on('focusout', function () {
        if (!$input.validator.is_valid()) {
            input.css('border', '1px solid #ff0000');
            input.focus().select();
        } else {
            input.css('border', '1px solid #DBDBDB');
        }
    });
    let sortable = Sortable.create(milestone_ul.get(0), {
        handle: '.fa-arrows-v',
        animation: 150,
        ghostClass: 'blue-background-class',

    });

    milestone_ul.next('input').bind('keypress', function (event) {
        let input = $(this);
        let project_id = input[0].id.split('milestoneNameInput')[1];
        if (event.keyCode === 13) {
            add_milestone_or_category(project_id, 'milestone');
        }
    });

    category_ul.next('input').bind('keypress', function (event) {
        let input = $(this);
        let project_id = input[0].id.split('categoryNameInput')[1];
        if (event.keyCode === 13) {
            add_milestone_or_category(project_id, 'category');
        }
    });

    if (milestone_ul.attr('data-old-order')) {
        let old_order = milestone_ul.attr('data-old-order').split(',');
        sortable.sort(old_order);
    } else {
        milestone_ul.attr('data-old-order', sortable.toArray());
    }
    if (!color_picker.attr('data-color')) {
        Register_color_picker(project_id);
    }
    select_users.find('input[name=normal_user]').prop('checked', false);
    select_users.find('input[name=project_user]').prop('checked', true);
    $('#filter_by_tag' + project_id).val('-1');
    $('#select_users' + project_id).children('label[data-tag_id]').show();
    milestone_ul.children('li').show();
    category_ul.children('li').show();
    $('#filter_by_tag' + project_id).change(function () {
        TagFilter(project_id);
    });
    $('#EditProjectModal' + project_id).attr('data-backdrop', 'static').modal('show');
}

function TagFilter(project_id) {
    let tag_val = $('#filter_by_tag' + project_id + ' option:selected').val();
    let user_checkboxes = $('#select_users' + project_id).children('label[data-tag_id]');
    if (tag_val === '-1') {
        user_checkboxes.show();
        return;
    } else {
        user_checkboxes.hide();
        user_checkboxes.each(function () {
            let ele = $(this);
            let ele_val = ele.attr('data-tag_id');
            if (ele_val === tag_val)
                ele.show();
        });
    }
}

function project_modal_save(project_id) {
    let $project_title_input = $('#project_title_input' + project_id);
    let input = new Input($project_title_input);
    $project_title_input.trigger('change');
    if (!input.validator.is_valid()) {
        layer.msg('Project name is invalid, Please check out your input carefully !', {
            skin: 'layer-error-skin',
            area: ['430px', 'auto'],
            offset: '100px',
            time: 1000,
            end: function () {
                $project_title_input.css('border', '1px solid #ff0000');
                $project_title_input.focus().select();
            }
        });
        return
    }
    let project_title = $project_title_input.val();
    let exist_milestones_id_title = {};
    let order_id_array = [];
    let milestone_ul = $('#milestone_ul' + project_id);
    let category_ul = $('#category_ul' + project_id);
    let select_users = $('#select_users' + project_id);
    milestone_ul.children('li:visible').each(function () {
        let id = $(this)[0].id.split('milestone_li')[1];
        order_id_array.push(id);
        let title = $(this).children('span[name=milestone_title_span]').text();
        exist_milestones_id_title[id] = title;
    });
    let milestone_input = milestone_ul.next('input');
    milestone_input.on('change', function () {
        $(this).css('border', '1px solid #dbdbdb');
    });
    if ($.isEmptyObject(exist_milestones_id_title)) {
        layer.msg('At least one milestone is required !', {
            skin: 'layer-error-skin',
            time: 1000,
            offset: '100px',
            end: function () {
                milestone_input.css('border', '1px solid #ff0000');
                milestone_input.focus().select();
            }
        });
        return
    }
    let wait_to_delete_milestone_id_array = [];
    milestone_ul.children('li[name=forever]:hidden').each(function () {
        let id = $(this)[0].id.split('milestone_li')[1];
        wait_to_delete_milestone_id_array.push(id);
    });

    let exist_categories_id_title_color = {};
    category_ul.children('li:visible').each(function () {
        let id = $(this)[0].id.split('category_li')[1];
        let title = $(this).children('span[name=category_title_span]').text();
        let color = $(this).attr('style').split(';')[1].replace('background:', '');
        exist_categories_id_title_color[id] = {
            'title': title,
            'color': color
        };
    });

    let wait_to_delete_category_id_array = [];
    category_ul.children('li[name=forever]:hidden').each(function () {
        let id = $(this)[0].id.split('category_li')[1];
        wait_to_delete_category_id_array.push(id);
    });

    let wait_remove_users_id_array = [];
    select_users.find('input[name=project_user]').each(function () {
        if (!$(this).is(':checked')) {
            let id = $(this)[0].id.split('inlineCheckbox')[1];
            wait_remove_users_id_array.push(id);
        }
    });

    let wait_add_users_id_array = [];
    select_users.find('input').each(function () {
        if ($(this).is(':checked')) {
            let id = $(this)[0].id.split('inlineCheckbox')[1];
            wait_add_users_id_array.push(id);
        }
    });

    let data_json = {
        'project_id': project_id,
        'project_title': project_title,
        'order_id_array': order_id_array,
        'exist_milestones_id_title': exist_milestones_id_title,
        'wait_to_delete_milestone_id_array': wait_to_delete_milestone_id_array,
        'exist_categories_id_title_color': exist_categories_id_title_color,
        'wait_to_delete_category_id_array': wait_to_delete_category_id_array,
        'wait_remove_users_id_array': wait_remove_users_id_array,
        'wait_add_users_id_array': wait_add_users_id_array
    };

    $.ajax({
        type: "post",
        url: "{{ url_for('setting.save_project_edit_modal') }}",
        contentType: "application/json;charset=utf-8",
        data: JSON.stringify(data_json),
        success: function (status) {
            if (status !== 'fail') {
                $('#EditProjectModal' + project_id).modal('hide');
                if (status === 'edit')
                    layer.msg('修改成功！');
                else if (status === 'add')
                    layer.msg('添加成功！');
                socket.emit('refresh');
                setTimeout(function () {
                    parent.location.reload();
                }, 1000);
            } else {
                layer.msg('修改失败，请稍后再试！')
            }
        },
        error: function (error) {
            console.log(error);
        },
        complete: function () {

        }
    });
}