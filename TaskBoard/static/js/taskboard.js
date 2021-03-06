let size = {
    width: window.innerWidth || document.body.clientWidth,
    height: window.innerHeight || document.body.clientHeight
};
let project_Reg = new RegExp('project_node');
let milestone_Reg = new RegExp('milestone_node');
let task_Reg = new RegExp('task_node');


function GenerateLabelByNode(node) {
    let node_id = $(node)[0].id;
    let label = 'Add';
    if (milestone_Reg.test(node_id))
        label = 'Add Task';
    else if (project_Reg.test(node_id))
        label = 'Add MileStone';
    return label;
}

function disableUnformatPaste(node) {
    let node_id = $(node)[0].id;
    let tree = $(node).jstree(true);
    let paste_buffer;
    if (tree.can_paste()) {
        paste_buffer = tree.get_buffer();
        let paste_buffer_id = paste_buffer.node[0].id;
        if (task_Reg.test(paste_buffer_id)) {
            if (milestone_Reg.test(node_id)) {
                return false;
            }
        }
        if (milestone_Reg.test(paste_buffer_id)) {
            if (project_Reg.test(node_id)) {
                return false;
            }
        }
    }
    return true;
}

function customMenu(node) {
    let items = {
        "cut": {
            "separator_before": false,
            "icon": "fa fa-scissors",
            "separator_after": false,
            "label": "Cut",
            "action": function (data) {
                let inst = $.jstree.reference(data.reference),
                    obj = inst.get_node(data.reference);
                if (inst.is_selected(obj)) {
                    inst.cut(inst.get_top_selected());
                } else {
                    inst.cut(obj);
                }
            }
        },
        "copy": {
            "separator_before": false,
            "icon": 'fa fa-clone',
            "separator_after": false,
            "label": "Copy",
            "action": function (data) {
                let inst = $.jstree.reference(data.reference),
                    obj = inst.get_node(data.reference);
                if (inst.is_selected(obj)) {
                    inst.copy(inst.get_top_selected());
                } else {
                    inst.copy(obj);
                }
            }
        },
        "paste": {
            "separator_before": false,
            "icon": "fa fa-clipboard",
            "_disabled": disableUnformatPaste(node),
            "separator_after": false,
            "label": "Paste",
            "action": function (data) {
                let inst = $.jstree.reference(data.reference),
                    obj = inst.get_node(data.reference);
                let node_buffer = inst.get_buffer();
                let mode = node_buffer.mode;
                let node_id = node_buffer.node[0].id;
                let type_and_id = getTypeAndId(node_id);
                let node_type = type_and_id.node_type;
                let id = type_and_id.id;
                let target_id_text = $(node)[0].id;
                let target_id = getTypeAndId(target_id_text).id
                let buffer_node = node_buffer.node;
                let name = buffer_node[0].text;
                if (mode === 'move_node') {
                    $.ajax({
                        url: "{{ url_for('taskboard.move_node') }}",
                        type: 'POST',
                        data: {
                            'type': node_type,
                            'id': id,
                            'target_id': target_id
                        },
                        success: function (e) {
                            if (e === 'ok') {
                                socket.emit('refresh');
                                layer.msg(node_type + ' ' + name + '移动成功！');
                            } else {
                                layer.msg('Move failed！');
                                return;
                            }
                            inst.refresh();
                            AjaxReloadPageAfterContextMenu(node_type, id, "paste");
                        },
                        error: function (error) {
                            layer.msg('Something wrong in server！');
                            console.log(error);
                        },
                    });
                } else if (mode === 'copy_node') {
                    let icon = 'fa fa-maxcdn';
                    if (node_type === 'task')
                        icon = 'fa fa-tumblr';
                    let node_json = {'text': node_buffer.node[0].text, 'icon': icon};
                    inst.create_node(obj, node_json, "last", function (new_node) {
                        try {
                            inst.edit(new_node, null, function (ob) {
                                let new_name = ob.text;
                                $.ajax({
                                    url: "{{ url_for('taskboard.copy_node') }}",
                                    type: 'POST',
                                    data: {
                                        'type': node_type,
                                        'id': id,
                                        'new_name': new_name,
                                        'target_id': target_id
                                    },
                                    success: function (e) {
                                        let status = e.split('-')[0];
                                        let new_node_id = e.split('-')[1];
                                        if (status === 'ok') {
                                            socket.emit('refresh');
                                            layer.msg(node_type + ' ' + name + '复制成功！');
                                        } else {
                                            layer.msg('Copy failed！');
                                            return;
                                        }
                                        inst.refresh();
                                        AjaxReloadPageAfterContextMenu(node_type, new_node_id, "paste");
                                    },
                                    error: function (error) {
                                        layer.msg('Something wrong in server！');
                                        console.log(error);
                                    },
                                });
                            });
                        } catch (ex) {
                            setTimeout(function () {
                                inst.edit(new_node);
                            }, 0);
                        }
                    });
                }
            }
        },
        "add": {
            "separator_before": false,
            "icon": "fa fa-plus",
            "separator_after": false,
            "_disabled": false,
            "label": GenerateLabelByNode(node),
            "action": function (data) {
                if (data.item.label == 'Add Task') {
                    let milestone_id = node.id.split('milestone_node')[1];
                    // task_modal_show(node, 'add');
                    before_task_modal_show(milestone_id);
                    return;
                }
                let inst = $.jstree.reference(data.reference),
                    obj = inst.get_node(data.reference);
                inst.create_node(obj, {}, "last", function (new_node) {
                    try {
                        let parent_node_id_text = new_node.parent;
                        let parent_id = getTypeAndId(parent_node_id_text).id;
                        inst.edit(new_node, null, function (ob) {
                            let new_name = ob.text;
                            $.ajax({
                                url: "{{ url_for('taskboard.add_milestone_node') }}",
                                type: 'POST',
                                data: {
                                    'new_name': new_name,
                                    'parent_id': parent_id
                                },
                                success: function (e) {
                                    if (e === 'ok') {
                                        socket.emit('refresh');
                                        layer.msg('milestone ' + new_name + ' 修改成功！');
                                    } else {
                                        layer.msg('Add Milestone Failed！');
                                        return;
                                    }
                                    inst.refresh_node(obj);
                                    AjaxReloadPageAfterContextMenu('milestone', '', 'add milestone');
                                },
                                error: function (error) {
                                    layer.msg('Something wrong in server！');
                                    console.log(error);
                                },
                            });
                        });
                    } catch (ex) {
                        setTimeout(function () {
                            inst.edit(new_node);
                        }, 0);
                    }
                });
            }
        },
        "rename": {
            "separator_before": false,
            "icon": "fa fa-font",
            "separator_after": false,
            "_disabled": false,
            "label": "Rename",
            "action": function (data) {
                let inst = $.jstree.reference(data.reference),
                    obj = inst.get_node(data.reference);
                inst.edit(obj, null, function (ob) {
                    let new_name = ob.text;
                    let node_id = ob.id;
                    let type_and_id = getTypeAndId(node_id);
                    let id = type_and_id.id;
                    let node_type = type_and_id.node_type;
                    $.ajax({
                        url: "{{ url_for('taskboard.rename_node') }}",
                        type: 'POST',
                        data: {
                            'type': node_type,
                            'id': id,
                            'new_name': new_name
                        },
                        success: function (e) {
                            if (e === 'ok') {
                                socket.emit('refresh');
                                layer.msg(node_type + ' name 修改成功！');
                            } else {
                                layer.msg('Rename failed！');
                                return;
                            }
                            inst.refresh_node(obj);
                            AjaxReloadPageAfterContextMenu(node_type, id, 'rename');
                        },
                        error: function (error) {
                            layer.msg('Something wrong in server！');
                            console.log(error);
                        },
                    });
                });
            }
        },
        "remove": {
            "separator_before": false,
            "icon": "fa fa-trash-o",
            "separator_after": false,
            "_disabled": false,
            "label": "Delete",
            "action": function (data) {
                let inst = $.jstree.reference(data.reference),
                    obj = inst.get_node(data.reference);
                delete_node_or_task(obj);

            }
        },
        "create_project": {
            "separator_before": true,
            "icon": "fa fa-pinterest-p",
            "separator_after": false,
            "_disabled": false,
            "label": "New Project",
            "action": function () {
                show_project_edit_modal('');
            }
        }
    };
    let id = $(node)[0].id;
    let node_id;
    if (task_Reg.test(id)) {
        node_id = $('#' + id).parents('li[id^=project_node]')[0].id.split('project_node')[1];
    } else if (milestone_Reg.test(id)) {
        node_id = $('#' + id).parents('li[id^=project_node]')[0].id.split('project_node')[1];
    } else if (project_Reg.test(id)) {
        node_id = id.split('project_node')[1];
    }
    if ('{{ current_user.is_admin }}' !== 'True' && '{{ current_user.access_project_id }}' !== node_id)
        return {};
    if (task_Reg.test(id))
        delete items.add;
    if (project_Reg.test($(node)[0].id)) {
        delete items.copy;
        delete items.cut;
    }
    return items;
}

function getTypeAndId(node_id) {
    let type_and_id;
    let node_type, id;
    if (task_Reg.test(node_id)) {
        node_type = 'task';
        id = node_id.split('task_node')[1];
    } else if (milestone_Reg.test(node_id)) {
        node_type = 'milestone';
        id = node_id.split('milestone_node')[1];
    } else if (project_Reg.test(node_id)) {
        node_type = 'project';
        id = node_id.split('project_node')[1];
    }
    type_and_id = {'id': id, 'node_type': node_type}
    return type_and_id;
}


function AjaxReloadPageAfterContextMenu(node_type, id, action) {
    let project_id = $('#store_project_id_for_ajax').text();
    let task_id = $('#store_task_id_for_ajax').text();
    let is_show_milestone_array = [];
    $('.layui-show').each(function () {
        is_show_milestone_array.push($(this)[0].id.split('layui_colla_content')[1]);
    });
    if (node_type === 'project') {
        if (action === 'delete') {
            $('#milestone-panel-body').children().remove();
            $('#task-panel-body').children().remove();
        } else {
            LoadMileStone(project_id, true, is_show_milestone_array);
            LoadTaskById(task_id);
        }
    } else if (node_type === 'milestone') {
        if (action === 'delete') {
            is_show_milestone_array.splice(is_show_milestone_array.indexOf(id), 1);
        }
        LoadMileStone(project_id, true, is_show_milestone_array);
        LoadTaskById('');
    } else if (node_type === 'task') {
        if (action === 'delete') {
            task_id = '';
        }
        LoadMileStone(project_id, true, is_show_milestone_array);
        LoadTaskById(task_id);
    }
}

function TreeNodeClickEvent(data) {
    let node = data.node;
    let id = node.id;
    let project_node;
    let project_id;
    let milestone_node_id = 'None';
    if (task_Reg.test(id)) {
        LoadTaskById(id.split('task_node')[1]);
        project_node = $('#' + id).parents('li[id^=project_node]');
        project_id = project_node[0].id.split('project_node')[1];
        milestone_node_id = $('#' + id).parents('li[id^=milestone_node]')[0].id.split('milestone_node')[1];
    } else if (milestone_Reg.test(id)) {
        project_node = $('#' + id).parents('li[id^=project_node]');
        project_id = project_node[0].id.split('project_node')[1];
        milestone_node_id = id.split('milestone_node')[1];
    } else if (project_Reg.test(id)) {
        project_id = id.split('project_node')[1];
    } else {
        return;
    }
    let tree = $('#tree-panel-body').jstree(true);
    tree.open_node(node);
    LoadMileStone(project_id, true, [milestone_node_id]);
}

function whether_show_add_button() {
    let is_no_project = $('#tree-panel-body').children('.jstree-container-ul.jstree-children.jstree-contextmenu')[0].hasChildNodes();
    if (!is_no_project) {
        $('#add_project_when_none').show();
        $('#board_container').load('{{ url_for("taskboard.none_project") }}');
    }
}

function LoadTree() {
    $('#tree-panel-body').jstree({
        'core': {
            'data': {
                'url': '{{ url_for("taskboard.tree_json") }}'
            },
            "themes": {
                "variant": "large"
            },
            'check_callback': true,
        },
        'plugins': ['contextmenu'],
        "contextmenu": {
            'items': customMenu
        }
    }).on("select_node.jstree", function (e, data) {
        TreeNodeClickEvent(data);
    }).on('refresh.jstree', whether_show_add_button).on('loaded.jstree', whether_show_add_button);
}

function LoadMileStone(project_id, show, milestone_node_id_array) {
    $('#milestone-panel-body').load('{{ url_for("taskboard.render_milestone_column") }}', {'project_id': project_id}, function () {
        $('div[id^=task_card]').on('click', LoadTaskColumn);
        if (show) {
            for (let i = 0; i < milestone_node_id_array.length; i++) {
                $('#layui_colla_content' + milestone_node_id_array[i]).addClass('layui-show');
            }
        }
        $('.layui-collapse').css('height', size.height - 50 - 38 - 60);
        setLineWidthByClass('project');
        layui.use('element', function () {
            layui.element.init();
        });
    });
}

function LoadTaskById(task_id) {
    if (task_id === '') {
        $('#task-panel-body').children().remove();
        return;
    }
    $('#task-panel-body').load('{{ url_for("taskboard.render_task_column") }}', {'task_id': task_id}, function () {
        setLineWidthByClass('task');
        Register_time_tip();
        $('.task_column_panel').css('height', size.height - 50 - 38 - 60);
        layui.use('element', function () {
            layui.element.init();
        });
        layui.use('upload', function () {
            let upload = layui.upload;
            let upload_ele = $('#upload_attachment');
            upload.render({
                elem: upload_ele,
                url: "{{ url_for('taskboard.task_attachment_upload') }}",
                field: 'attachment',
                data: {'task_id': task_id},
                auto: false,
                size: 10000,
                accept: 'file', //普通文件
                //exts: 'zip|rar|7z|txt|doc|docx',
                bindAction: '#upload_btn',
                done: function (res) {
                    socket.emit('refresh');
                    layer.msg("File Upload Success");
                    let tree = $('#tree-panel-body').jstree(true);
                    let node = tree.get_node('#task_node' + task_id);
                    tree.deselect_node(tree.get_selected()[0]);
                    tree.select_node(node);
                }
            });
        });
    });
}

function LoadTaskColumn() {
    let ele = this;
    let task_id = ele.id.split('task_card')[1];
    LoadTaskById(task_id);
}

function setLineWidthByClass(css_class) {
    let ele_title = $('.' + css_class + '_title');
    let title = ele_title.children('.title');
    let width = (parseInt(ele_title.css('width')) - parseInt(title.css('width')) - 10) / 2;
    ele_title.children('.line').css('width', width);
}


function Register_time_tip() {
    let tip_index;
    $('[name=moment_tip]').hover(function () {
        let ele = $(this);
        let time = moment(ele.data('timestamp')).format('LLL');
        tip_index = layer.tips(
            'Create at ' + time,
            ele, {
                tips: [1, '#2b2b2b'],
            });
    }, function () {
        layer.close(tip_index);
    })
}

function before_task_modal_show(milestone_id) {
    $('#store_milestone_id_when_add_task').text(milestone_id);
    $('#load_task_add_modal').load('{{ url_for("taskboard.render_task_add_modal") }}', {'milestone_id': milestone_id}, function () {
        task_modal_show({id: 'milestone_node' + milestone_id}, 'add');
    });
}

function before_task_edit_modal_show(node, action, data) {
    let milestone_id = node.id.split('milestone_node')[1];
    $('#load_task_add_modal').load('{{ url_for("taskboard.render_task_add_modal") }}', {'milestone_id': milestone_id}, function () {
        task_modal_show(node, action, data);
    });
}

function task_modal_show(node, action, data) {
    let input = $('#task_title_input');
    let input_error = $('#task_title-input-error');
    let $input = new Input(input);
    let description_input = $('#task_add_modal_textarea');
    input.on('focusout', function () {
        if (!$input.validator.is_valid()) {
            input.css('border', '1px solid #ff0000');
            input.focus().select();
            input_error.show();
        } else {
            input.css('border', '1px solid #DBDBDB');
            input_error.hide();
        }
    });
    let id = node.id.split('milestone_node')[1];
    $('#store_milestone_id_when_add_task').text(id);
    input.val('');
    description_input.val('');
    $('#milestone_select_' + id).attr('selected', 'selected');
    if (action === 'edit') {
        $('#add_or_edit_task').text('Edit Task');
        $('#task_submit_button').text('Save Changes');
        input.val($('#task_title').text());
        description_input.val($('#task_description').text());
        $('#user_select_' + data.user_id).attr('selected', 'selected');
        $('#category_select_' + data.category_id).attr('selected', 'selected');
        $('#milestone_select_' + data.milestone_id).attr('selected', 'selected');
        $('#color_text').val(data.color);
        $('#task_points').val(data.points);
    }
    let ele = $('#Color_picker');
    layui.use('colorpicker', function () {
        let colorpicker = layui.colorpicker;
        colorpicker.render({
            elem: ele,
            color: '#D9EDF7',
            size: 'lg',
            predefine: true,
            colors: ['#dff0d8', '#d9edf7', '#fcf8e3', '#f2dede', '#337ab7'],
            change: function (color) {
                $('#color_text').val(color);
            }
        });
    });
    layui.use('laydate', function () {
        let today = new Date();
        let dd = today.getDate();
        let mm = today.getMonth() + 1;
        if (parseInt(mm) < 10)
            mm = '0' + mm;
        let yyyy = today.getFullYear();
        let today_date = `${yyyy}-${mm}-${dd}`;
        $('#date_picker').val(today_date);
        let render_value = today_date
        if (action === 'edit') {
            render_value = data.due_date;
            $('#date_picker').val(render_value);
        }
        let laydate = layui.laydate;
        laydate.render({
            elem: '#date_picker',
            lang: 'en',
            type: 'date',
            value: render_value,
            min: 0,
            btns: ['now', 'confirm'],
            done: function (value, date, endDate) {
                $('#date_picker').val(value);
            }
        });
    });
    $('#EditTaskModal').attr('data-backdrop', 'static').modal('show');
}

function task_modal_save() {
    let $task_title_input = $('#task_title_input');
    let input = new Input($task_title_input);
    $task_title_input.trigger('change');
    if (!input.validator.is_valid()) {
        layer.msg('Task name is invalid, Please check out your input carefully !', {
            skin: 'layer-error-skin',
            offset: '100px',
            area: ['430px', 'auto'],
            time: 1000,
            end: function () {
                $task_title_input.css('border', '1px solid #ff0000');
                $task_title_input.focus().select();
            }
        });
        return
    }
    let task_name = $('#task_title_input').val();
    let task_description = $('#task_add_modal_textarea').val();
    let assigned_user_id = $('#task_add_modal_user option:selected').val();
    let category_id = $('#task_add_modal_category option:selected').val();
    let milestone_id = $('#task_add_modal_milestone option:selected').val();
    let color_text = $('#color_text').val();
    if (!color_text)
        color_text = '#D9EDF7';
    let date_picker_text = $('#date_picker').val();
    let points = $('#task_points').val();
    let action_type = 'add';
    let task_id;
    if ($('#task_submit_button').text() === 'Save Changes') {
        task_id = $('#store_task_id_for_ajax').text();
        action_type = 'edit';
    }
    let data_json = {
        action_type: action_type,
        task_id: task_id,
        task_name: task_name,
        task_description: task_description,
        assigned_user_id: assigned_user_id,
        category_id: category_id,
        milestone_id: milestone_id,
        color_text: color_text,
        date_picker_text: date_picker_text,
        points: points
    };

    $.ajax({
        type: "post",
        url: "{{ url_for('taskboard.save_task_edit_modal') }}",
        contentType: "application/json;charset=utf-8",
        data: JSON.stringify(data_json),
        success: function (status_id) {
            let status = status_id.split('-')[0];
            let id = status_id.split('-')[1];
            if (status !== 'fail') {
                $('#EditTaskModal').modal('hide');
                if (status === 'edit')
                    layer.msg('修改成功！');
                else if (status === 'add')
                    layer.msg('添加成功！');
                socket.emit('refresh');
                let tree = $('#tree-panel-body').jstree(true);

                let select_node = tree.get_selected()[0];
                tree.deselect_node(select_node);
                tree.refresh();
                let is_show_milestone_array = [];
                $('.layui-show').each(function () {
                    is_show_milestone_array.push($(this)[0].id.split('layui_colla_content')[1]);
                });
                setTimeout(function () {
                    let task_node = tree.get_node('#task_node' + id);
                    tree.select_node(task_node);
                    setTimeout(function () {
                        for (let i = 0; i < is_show_milestone_array.length; i++) {
                            $('#layui_colla_content' + is_show_milestone_array[i]).addClass('layui-show');
                        }
                    }, 100);
                }, 700);
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

function edit_task_comment(the, comment_id) {
    let h4 = $('#add_comment_h4');
    let textarea_submit_btn = $('#comment_textarea_submit');
    let textarea_cancel_btn = $('#comment_textarea_cancel');
    let comment_text = $('#comment_text' + comment_id).children('span');
    let textarea = $('#comment_textarea');
    $('#store_comment_id').val(comment_id);  // 存储comment 的 id
    h4.text('Edit Comment');
    textarea_submit_btn.children('span').text(' Edit Comment');
    textarea.val(comment_text.text());
    textarea_cancel_btn.show();
}

function edit_comment_cancel() {
    let h4 = $('#add_comment_h4');
    let textarea_submit_btn = $('#comment_textarea_submit');
    let textarea_cancel_btn = $('#comment_textarea_cancel');
    let textarea = $('#comment_textarea');
    $('#store_comment_id').val('add');
    h4.text('Add Comment');
    textarea_submit_btn.children('span').text(' Submit Comment');
    textarea.val('');
    textarea_cancel_btn.hide();
}

function submit_comment(the, task_id) {
    let val = $('#store_comment_id').val();
    let action = 'add';
    let comment_id;
    if (val !== 'add') {
        action = 'edit'
        comment_id = val;
    }
    let comment_textarea = $('#comment_textarea');
    if (comment_textarea.val() === '') {
        layer.msg('Please input comment !');
        return;
    }
    $.ajax({
        url: "{{ url_for('taskboard.edit_or_add_comment') }}",
        type: 'POST',
        data: {
            'action': action,
            'task_id': task_id,
            'comment_id': comment_id,
            'text': comment_textarea.val()
        },
        success: function (e) {
            if (e === 'edit') {
                socket.emit('refresh');
                layer.msg('Comment 修改成功！');
            } else if (e === 'add') {
                socket.emit('refresh');
                layer.msg('Comment 增加成功！');
            } else {
                layer.msg('Submit failed！');
                return;
            }
            setTimeout(() => {
                LoadTaskById(task_id);
            }, 300);
        },
        error: function (error) {
            layer.msg('Something wrong in server！');
            console.log(error);
        },
    });

}

function delete_node_or_task(obj) {
    let node_id = obj.id;
    let type_and_id = getTypeAndId(node_id);
    let id = type_and_id.id;
    let node_type = type_and_id.node_type;
    let name = obj.text;
    let layer_title = node_type.charAt(0).toUpperCase() + node_type.slice(1);
    let layer_content = '<div class="text-center" style="margin-top:20px"><p>Are you sure to delete ' + node_type + ' <span class="label label-danger">' +
        name + '</span> ?</p></div>';
    if (node_type === 'project')
        layer_content += '<div class="text-center" style="margin-top:20px;   color:red;"><p>Warning: Everything of this project will be removed !</p></div>';
    if (node_type === 'milestone')
        layer_content = layer_content + '<div class="text-center" style="margin-top:20px;   color:red;"><p>Warning: All task in this milestone will also be removed !</p></div>';
    if (node_type === 'task')
        layer_content += '<div class="text-center" style="margin-top:20px;   color:red;"><p>Warning: Comment and Files belongs to this task will also be removed !</p></div>';
    layer.open({
        type: 1,
        skin: "layui-layer-rim",
        area: ['400px', '200px'],
        title: 'Delete ' + layer_title,
        content: layer_content,
        btn: ['删除', '取消'],
        anim: 6,
        offset: '150px',
        yes: function (index) {
            $.ajax({
                url: "{{ url_for('taskboard.delete_node') }}",
                type: 'POST',
                data: {
                    'type': node_type,
                    'id': id,
                },
                success: function (e) {
                    layer.close(index);
                    if (e === 'ok') {
                        socket.emit('refresh');
                        let inst = $('#tree-panel-body').jstree(true);
                        if (inst.is_selected(obj.id)) {
                            inst.delete_node(inst.get_selected());
                        } else {
                            inst.delete_node(obj.id);
                        }
                        layer.msg(node_type + " : " + name + ' 删除成功！');
                        inst.refresh();
                        setTimeout(function () {
                            AjaxReloadPageAfterContextMenu(node_type, id, 'delete');
                        }, 500);
                    } else {
                        layer.msg('删除失败！');
                        return;
                    }
                },
                error: function (error) {
                    layer.msg('Something wrong in server！');
                    console.log(error);
                },
            });
        },
        btn2: function (index) {
            layer.close(index);
        }
    });
}

function delete_task_attachment(the, file_id, file_source_name, file_security_name, task_id) {
    layer.open({
        type: 1,
        skin: "layui-layer-rim",
        area: ['400px', '200px'],
        title: '删除附件',
        content: '<div class="text-center" style="margin-top:20px"><p>是否确定删除文件 <span class="label label-danger">' +
            file_source_name + '</span> ?</p></div>',
        btn: ['删除', '取消'],
        anim: 6,
        offset: '150px',
        yes: function (index) {
            $.ajax({
                url: "{{ url_for('taskboard.delete_task_attachment') }}",
                type: 'POST',
                data: {
                    file_id: file_id,
                    file_security_name: file_security_name,
                },
                success: function (e) {
                    if (e === 'ok') {
                        socket.emit('refresh');
                        layer.close(index);
                        layer.msg('删除成功！');
                        setTimeout(() => {
                            LoadTaskById(task_id);
                        }, 300);
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

function delete_task_comment(the, comment_id, task_id) {
    layer.open({
        type: 1,
        skin: "layui-layer-rim",
        area: ['400px', '200px'],
        title: '删除评论',
        content: '<div class="text-center" style="margin-top:20px"><p>是否确定删除此条评论 ?</p></div>',
        btn: ['删除', '取消'],
        anim: 6,
        offset: '150px',
        yes: function (index) {
            $.ajax({
                url: "{{ url_for('taskboard.delete_comment_by_id') }}",
                type: 'POST',
                data: {
                    'comment_id': comment_id,
                },
                success: function (e) {
                    if (e === 'ok') {
                        socket.emit('refresh');
                        layer.close(index);
                        layer.msg('删除成功！');
                        setTimeout(() => {
                            AjaxReloadPageAfterContextMenu('task', task_id, '');
                        }, 300);
                    } else {
                        layer.msg('删除失败！')
                    }
                },
                error: function (error) {
                    layer.msg('Something wrong in server！');
                    console.log(error);
                },
            });
        },
        btn2: function (index) {
            layer.close(index);
        }
    });

}

function complete_task(task_id) {
    layer.open({
        type: 1,
        skin: "layui-layer-rim",
        area: ['400px', '200px'],
        title: '完成任务',
        content: '<div class="text-center" style="margin-top:20px"><p>确定该任务已完成 ?</p></div>',
        btn: ['确定', '取消'],
        anim: 1,
        offset: '150px',
        yes: function (index) {
            $.ajax({
                url: "{{ url_for('taskboard.complete_task_by_id') }}",
                type: 'POST',
                data: {
                    'task_id': task_id,
                },
                success: function (e) {
                    if (e === 'ok') {
                        socket.emit('refresh');
                        layer.close(index);
                        layer.msg('Success！');
                        setTimeout(() => {
                            AjaxReloadPageAfterContextMenu('task', task_id, '');
                        }, 300);
                    } else {
                        layer.msg('Failed！')
                    }
                },
                error: function (error) {
                    layer.msg('Something wrong in server！');
                    console.log(error);
                },
            });
        },
        btn2: function (index) {
            layer.close(index);
        }
    });
}
