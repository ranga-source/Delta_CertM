import React, { useEffect } from 'react';
import { Modal, Form, Input, Switch, message } from 'antd';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../../services/api';
import { API_ENDPOINTS } from '../../../config/api.config';
import { QUERY_KEYS } from '../../../services/queryClient';
import { Tenant } from '../../../types/models.types';

interface TenantFormModalProps {
    visible: boolean;
    onCancel: () => void;
    editingTenant?: Tenant | null;
}

export const TenantFormModal: React.FC<TenantFormModalProps> = ({
    visible,
    onCancel,
    editingTenant
}) => {
    const [form] = Form.useForm();
    const queryClient = useQueryClient();
    const isEditing = !!editingTenant;

    useEffect(() => {
        if (visible) {
            if (editingTenant) {
                form.setFieldsValue({
                    name: editingTenant.name,
                    contact_email: editingTenant.contact_email,
                    is_active: editingTenant.is_active
                });
            } else {
                form.resetFields();
                form.setFieldsValue({ is_active: true });
            }
        }
    }, [visible, editingTenant, form]);

    const mutation = useMutation({
        mutationFn: async (values: any) => {
            if (isEditing) {
                await apiClient.put(`${API_ENDPOINTS.tenants}/${editingTenant.id}`, values);
            } else {
                await apiClient.post(API_ENDPOINTS.tenants, values);
            }
        },
        onSuccess: () => {
            message.success(`Tenant ${isEditing ? 'updated' : 'created'} successfully`);
            queryClient.invalidateQueries({ queryKey: QUERY_KEYS.tenants });
            onCancel();
        },
        onError: (error: any) => {
            message.error(`Failed to ${isEditing ? 'update' : 'create'} tenant: ${error?.response?.data?.detail || 'Unknown error'}`);
        },
    });

    const handleOk = () => {
        form.validateFields().then(values => {
            mutation.mutate(values);
        });
    };

    return (
        <Modal
            title={isEditing ? "Edit Tenant" : "Add Tenant"}
            open={visible}
            onOk={handleOk}
            onCancel={onCancel}
            confirmLoading={mutation.isPending}
            destroyOnClose
        >
            <Form
                form={form}
                layout="vertical"
                initialValues={{ is_active: true }}
            >
                <Form.Item
                    name="name"
                    label="Tenant Name"
                    rules={[{ required: true, message: 'Please enter tenant name' }]}
                >
                    <Input placeholder="Acme Corp" />
                </Form.Item>
                <Form.Item
                    name="contact_email"
                    label="Contact Email"
                    rules={[
                        { required: true, message: 'Please enter contact email' },
                        { type: 'email', message: 'Please enter a valid email' }
                    ]}
                >
                    <Input placeholder="admin@acme.com" />
                </Form.Item>
                {isEditing && (
                    <Form.Item
                        name="is_active"
                        label="Active Status"
                        valuePropName="checked"
                    >
                        <Switch />
                    </Form.Item>
                )}
            </Form>
        </Modal>
    );
};
