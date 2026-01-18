/**
 * Device Form Page
 * Create or edit device
 */

import { useEffect, useMemo } from 'react';
import { Card, Form, Input, Select, Button, message, Spin, Radio } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { useAppSelector } from '../../app/store';
import { Technology, Country } from '../../types/models.types';



function DeviceFormPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const currentTenantId = useAppSelector(state => state.tenant.currentTenantId);

  const { data: technologies } = useQuery({
    queryKey: QUERY_KEYS.technologies,
    queryFn: async () => {
      const response = await apiClient.get<Technology[]>(API_ENDPOINTS.technologies);
      return response.data;
    },
  });

  const { data: countries } = useQuery({
    queryKey: QUERY_KEYS.countries,
    queryFn: async () => {
      const response = await apiClient.get<Country[]>(API_ENDPOINTS.countries);
      return response.data;
    },
  });



  const { data: device, isLoading } = useQuery({
    queryKey: QUERY_KEYS.device(id || ''),
    queryFn: async () => {
      const response = await apiClient.get(`${API_ENDPOINTS.device(id!)}?tenant_id=${currentTenantId}`);
      return response.data;
    },
    enabled: !!id,
  });

  useEffect(() => {
    if (device) {
      console.log('DEBUG: Device Loaded:', device);
      console.log('DEBUG: Target Countries raw:', device.target_countries);

      form.resetFields();

      const targetCountries = device.target_countries || ['ALL'];
      const isSpecific = Array.isArray(targetCountries) &&
        targetCountries.length > 0 &&
        targetCountries[0] !== 'ALL';

      console.log('DEBUG: isSpecific:', isSpecific);

      form.setFieldsValue({
        ...device,
        technology_ids: device.technologies?.map((t: any) => t.id),
        target_market_type: isSpecific ? 'SPECIFIC' : 'ALL',
        target_countries: isSpecific ? targetCountries : ['ALL']
      });
    }
  }, [device, form]);

  const mutation = useMutation({
    mutationFn: async (values: any) => {
      if (id) {
        return apiClient.put(`${API_ENDPOINTS.device(id)}?tenant_id=${currentTenantId}`, values);
      }
      return apiClient.post(`${API_ENDPOINTS.devices}?tenant_id=${currentTenantId}`, values);
    },
    onSuccess: () => {
      message.success(id ? 'Device updated successfully' : 'Device created successfully');
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.devices(currentTenantId || '') });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceRecords(currentTenantId || '') });
      if (id) {
        queryClient.invalidateQueries({ queryKey: QUERY_KEYS.device(id) });
      }
      navigate('/devices');
    },
  });

  if (isLoading && id) return <Spin />;

  return (
    <Card title={id ? 'Edit Device' : 'Add Device'}>
      <Form
        form={form}
        layout="vertical"
        onFinish={(values) => mutation.mutate(values)}
        style={{ maxWidth: 600 }}
      >
        <Form.Item
          name="model_name"
          label="Model Name"
          rules={[{ required: true, message: 'Please enter model name' }]}
        >
          <Input placeholder="e.g., Tractor X9" />
        </Form.Item>

        <Form.Item name="sku" label="SKU">
          <Input placeholder="e.g., TRX9-2024" />
        </Form.Item>

        <Form.Item name="description" label="Description">
          <Input.TextArea rows={4} placeholder="Device description..." />
        </Form.Item>

        <Form.Item
          name="technology_ids"
          label="Technologies"
          rules={[{ required: true, message: 'Please select at least one technology' }]}
        >
          <Select
            mode="multiple"
            showSearch
            placeholder="Select technologies"
            optionFilterProp="label"
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            options={technologies?.map(tech => ({
              label: tech.name,
              value: tech.id,
            }))}
          />
        </Form.Item>

        {/* Target Markets Selection */}
        <Form.Item label="Target Markets" required>
          <Form.Item name="target_market_type" noStyle>
            <Radio.Group onChange={(e) => {
              if (e.target.value === 'ALL') {
                form.setFieldValue('target_countries', ['ALL']);
              } else {
                form.setFieldValue('target_countries', []);
              }
            }}>
              <Radio value="ALL">Global (All Countries)</Radio>
              <Radio value="SPECIFIC">Select Specific Markets</Radio>
            </Radio.Group>
          </Form.Item>
        </Form.Item>

        <Form.Item
          noStyle
          shouldUpdate={(prev, curr) => prev.target_market_type !== curr.target_market_type}
        >
          {({ getFieldValue }) =>
            getFieldValue('target_market_type') === 'SPECIFIC' ? (
              <Form.Item
                name="target_countries"
                label="Select Countries"
                rules={[{ required: true, message: 'Please select at least one country' }]}
              >
                <Select
                  mode="multiple"
                  showSearch
                  placeholder="Select target countries"
                  optionFilterProp="label"
                  options={countries?.map(c => ({
                    label: c.name,
                    value: c.iso_code
                  }))}
                  filterOption={(input, option) =>
                    (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                  }
                />
              </Form.Item>
            ) : null
          }
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={mutation.isPending}>
            {id ? 'Update' : 'Create'}
          </Button>
          <Button style={{ marginLeft: 8 }} onClick={() => navigate('/devices')}>
            Cancel
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
}

export default DeviceFormPage;


