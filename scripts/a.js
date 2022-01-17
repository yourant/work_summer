function() {
    let _item = SCOPE.list_model.selected_items[0];
    if (_item.state && _item.state !== 'running') {
        SCOPE.show_warning('只能操作审批中的流程,请重新选择')
    } else {
        dataService.callHcmOpenApi('workflow.get.process', {
            inst_id: _item.id
        }).then(function(_data) {
            console.log(_data);
            let assignment = _data['inst_detail'].assignment.filter(function(i) {
                return i.category == null
            });
            if (assignment && assignment.length === 0) {
                SCOPE.show_warning('未找到节点审批人')
            } else if (assignment && assignment.length === 1) {
                $hcDialog.simpleForm('确认待办事项', [{
                    'key': 'reason',
                    'label': '转办确认事项',
                    'component': 'hc-text-area',
                    'options': {
                        'placeholder': '请填写转办确认事项',
                        'required': true,
                        'rows': 8,
                        'width': 'col-12'
                    }
                }], {}, {
                    'size': 'small'
                }).then(function(_result) {
                    console.log(_result);
                    SCOPE.openSelectorDialog({
                        options: {
                            component: 'hc-tree-list-selector',
                            component_options: {
                                title: '选择器'
                            }
                        }
                    }, {
                        model: 'Employee',
                        role: 'sys-manager'
                    }).then(function(result) {
                        console.log(result);
                        dataService.callHcmOpenApi('workflow.node.turn.over', {
                            wf_inst_id: _item.id,
                            employee_id: result.id,
                            comment: _result.reason
                        }).then(function(data) {
                            if (data.success) {
                                SCOPE.show_warning('转办成功');
                                SCOPE.fetchData()
                            }
                        })
                    })
                })
            } else {
                let employee_radio_list = assignment.map(function(item) {
                    console.log(item);
                    return {
                        name: item.executor_name,
                        value: item.executor_id
                    }
                });
                $hcDialog.simpleForm('请选择被移交人', [{
                    'key': 'from_employee_id',
                    'component': 'hc-input-radio',
                    'options': {
                        'list': employee_radio_list,
                        'singleLine': false,
                        'required': true
                    }
                }], {}, {
                    'size': 'samll'
                }).then(function(emp_result) {
                    $hcDialog.simpleForm('确认待办事项', [{
                        'key': 'reason',
                        'label': '转办确认事项',
                        'component': 'hc-text-area',
                        'options': {
                            'placeholder': '请填写转办确认事项',
                            'required': true,
                            'rows': 8,
                            'width': 'col-12'
                        }
                    }], {}, {
                        'size': 'small'
                    }).then(function(_result) {
                        console.log(_result);
                        SCOPE.openSelectorDialog({
                            options: {
                                component: 'hc-tree-list-selector',
                                component_options: {
                                    title: '选择器'
                                }
                            }
                        }, {
                            model: 'Employee',
                            role: 'sys-manager'
                        }).then(function(result) {
                            console.log(result);
                            dataService.callHcmOpenApi('workflow.node.turn.over', {
                                wf_inst_id: _item.id,
                                employee_id: result.id,
                                from_employee_id: emp_result.from_employee_id,
                                comment: _result.reason
                            }).then(function(data) {
                                if (data.success) {
                                    SCOPE.show_warning('转办成功');
                                    SCOPE.fetchData()
                                } else {
                                    SCOPE.show_warning(data.msg)
                                }
                            })
                        })
                    })
                })
            }
        })
    }
}
