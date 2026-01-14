/**
 * Compliance Record Edit Page
 * Allows manual updates of status, expiry, certificate number, and document upload.
 */

import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, Form, Input, DatePicker, Select, Button, Space, Spin, Upload, message, Modal, Descriptions, Typography } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../services/api';
import { API_ENDPOINTS } from '../../config/api.config';
import { QUERY_KEYS } from '../../services/queryClient';
import { useAppSelector } from '../../app/store';
import { ComplianceRecord, ComplianceStatus, LabelingStatus } from '../../types/models.types';

function ComplianceRecordEditPage() {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { recordId } = useParams();
  const tenantId = useAppSelector(state => state.tenant.currentTenantId);
  const queryClient = useQueryClient();
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [labelUploadFile, setLabelUploadFile] = useState<File | null>(null);

  // Fetch existing record to prefill the form.
  const { data: record, isLoading } = useQuery({
    queryKey: QUERY_KEYS.complianceRecord(recordId || ''),
    queryFn: async () => {
      const response = await apiClient.get<ComplianceRecord>(
        `${API_ENDPOINTS.complianceRecord(recordId!)}?tenant_id=${tenantId}`
      );
      return response.data;
    },
    enabled: !!recordId && !!tenantId,
  });

  useEffect(() => {
    if (record) {
      form.setFieldsValue({
        status: record.status,
        labeling_status: record.labeling_status || LabelingStatus.PENDING,
        certificate_number: record.certificate_number,
        expiry_date: record.expiry_date ? dayjs(record.expiry_date) : null,
        doc_type: record.test_report_filename ? 'test_report' : 'certificate',
      });
    }
  }, [record, form]);

  // Update record mutation.
  const updateMutation = useMutation({
    mutationFn: async (values: any) => {
      const payload = {
        status: values.status,
        labeling_status: values.labeling_status,
        certificate_number: values.certificate_number || null,
        expiry_date: values.expiry_date ? (values.expiry_date as Dayjs).format('YYYY-MM-DD') : null,
      };
      await apiClient.put(
        `${API_ENDPOINTS.complianceRecord(recordId!)}?tenant_id=${tenantId}`,
        payload
      );
    },
    onSuccess: async () => {
      // Upload document if selected after successful update.
      if (uploadFile) {
        const formData = new FormData();
        formData.append('file', uploadFile);
        const docType = form.getFieldValue('doc_type') || 'certificate';
        await apiClient.post(
          `${API_ENDPOINTS.uploadDocument(recordId!)}?tenant_id=${tenantId}&doc_type=${docType}`,
          formData,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
          }
        );
      }

      // Upload label picture if selected
      if (labelUploadFile) {
        const formData = new FormData();
        formData.append('file', labelUploadFile);
        await apiClient.post(
          `${API_ENDPOINTS.uploadDocument(recordId!)}?tenant_id=${tenantId}&doc_type=label_picture`,
          formData,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
          }
        );
      }
    },
  });

  const handleSubmit = async (values: any) => {
    try {
      await updateMutation.mutateAsync(values);
      message.success('Compliance record updated');

      // Refresh caches
      await queryClient.invalidateQueries({ queryKey: ['complianceRecords'] });
      if (recordId) {
        await queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceRecords(tenantId || '') });
        await queryClient.invalidateQueries({ queryKey: QUERY_KEYS.complianceRecord(recordId) });
      }

      // Check for prompt condition (Status changed to ACTIVE from something else)
      const statusChangedToActive = values.status === ComplianceStatus.ACTIVE && record?.status !== ComplianceStatus.ACTIVE;

      if (statusChangedToActive && values.labeling_status !== LabelingStatus.DONE) {
        Modal.confirm({
          title: 'Labeling Requirements',
          content: 'Is the labeling for this certification completed? If yes, please mark Labeling Status as "Done" and upload proof before saving.',
          okText: 'Ok',
          cancelButtonProps: { style: { display: 'none' } },
        });
      } else {
        navigate('/compliance?tab=records');
      }
    } catch (error: any) {
      message.error(error?.response?.data?.detail || 'Failed to update record');
    }
  };

  if (isLoading) {
    return <Spin style={{ marginTop: 32 }} />;
  }

  if (!record) {
    return <Card title="Edit Compliance Record"><p>Record not found.</p></Card>;
  }

  return (
    <Card
      title="Edit Compliance Record"
      extra={<Button onClick={() => navigate(-1)}>Back</Button>}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        style={{ maxWidth: 600 }}
      >
        <div style={{ padding: '16px', background: '#fafafa', borderRadius: '8px', marginBottom: '24px', border: '1px solid #f0f0f0' }}>
          <Descriptions column={1} size="small">
            <Descriptions.Item label="Device"><strong>{record.device_name}</strong></Descriptions.Item>
            <Descriptions.Item label="Country">{record.country_name}</Descriptions.Item>
            <Descriptions.Item label="Certification">{record.certification_name}</Descriptions.Item>
          </Descriptions>
        </div>

        <Space style={{ width: '100%' }} align="start">
          <Form.Item label="Status" name="status" rules={[{ required: true, message: 'Select status' }]} style={{ flex: 1 }}>
            <Select
              options={[
                { label: 'Pending', value: ComplianceStatus.PENDING },
                { label: 'Active', value: ComplianceStatus.ACTIVE },
                { label: 'Expiring', value: ComplianceStatus.EXPIRING },
                { label: 'Expired', value: ComplianceStatus.EXPIRED },
              ]}
            />
          </Form.Item>

          <Form.Item noStyle shouldUpdate={(prevValues, currentValues) => prevValues.status !== currentValues.status}>
            {({ getFieldValue }) => (
              <Form.Item label="Labeling Status" name="labeling_status" style={{ flex: 1 }}>
                <Select
                  disabled={getFieldValue('status') !== ComplianceStatus.ACTIVE}
                  options={[
                    { label: 'Pending', value: LabelingStatus.PENDING },
                    { label: 'Done', value: LabelingStatus.DONE },
                  ]}
                />
              </Form.Item>
            )}
          </Form.Item>
        </Space>

        <Form.Item label="Document Type" name="doc_type" initialValue="certificate">
          <Select
            options={[
              { label: 'Certificate', value: 'certificate' },
              { label: 'Test Report', value: 'test_report' },
            ]}
            onChange={() => form.validateFields(['certificate_number', 'expiry_date', 'upload'])}
          />
        </Form.Item>

        <Form.Item noStyle shouldUpdate={(prev, curr) => prev.status !== curr.status || prev.labeling_status !== curr.labeling_status}>
          {({ getFieldsValue }) => {
            const { status, labeling_status } = getFieldsValue();
            if (status === ComplianceStatus.ACTIVE && labeling_status === LabelingStatus.DONE) {
              return (
                <div style={{ padding: '16px', background: '#e6f7ff', border: '1px solid #91d5ff', borderRadius: '8px', marginBottom: '24px' }}>
                  <Typography.Text type="secondary" style={{ display: 'block', marginBottom: 8, fontWeight: 'bold' }}>

                  </Typography.Text>
                  <Form.Item
                    label="Upload Labeling Proof (Optional)"
                    name="label_upload"
                    style={{ marginBottom: 0 }}
                  >
                    <Upload
                      beforeUpload={(file) => {
                        setLabelUploadFile(file);
                        form.validateFields(['label_upload']);
                        return false;
                      }}
                      onRemove={() => {
                        setLabelUploadFile(null);
                        form.validateFields(['label_upload']);
                      }}
                      maxCount={1}
                      fileList={labelUploadFile ? [labelUploadFile as any] : []}
                      accept="image/*,.pdf"
                    >
                      <Button icon={<UploadOutlined />}>Select Label Picture</Button>
                    </Upload>
                    {record.labeling_picture_filename && !labelUploadFile && (
                      <div style={{ marginTop: 8, fontSize: '12px', color: '#0050b3' }}>
                        <strong>Current Labeling Proof:</strong> {record.labeling_picture_filename}
                      </div>
                    )}
                  </Form.Item>
                </div>
              );
            }
            return null;
          }}
        </Form.Item>

        <Form.Item
          noStyle
          shouldUpdate={(prevValues, currentValues) => prevValues.doc_type !== currentValues.doc_type || prevValues.status !== currentValues.status}
        >
          {({ getFieldValue }) =>
            getFieldValue('doc_type') === 'certificate' ? (
              <>
                <Form.Item
                  label="Expiry Date"
                  name="expiry_date"
                  dependencies={['status']}
                  required={getFieldValue('status') === ComplianceStatus.ACTIVE}
                  rules={[
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (getFieldValue('status') === ComplianceStatus.ACTIVE && !value) {
                          return Promise.reject(new Error('Expiry date is required for Active status'));
                        }
                        if (value && (value as Dayjs).isBefore(dayjs().subtract(1, 'month'), 'day')) {
                          return Promise.reject(new Error('Expiry date cannot be more than 1 month in the past'));
                        }
                        return Promise.resolve();
                      },
                    }),
                  ]}
                >
                  <DatePicker
                    style={{ width: '100%' }}
                    disabledDate={(current) => current && current < dayjs().subtract(1, 'month').startOf('day')}
                  />
                </Form.Item>

                <Form.Item
                  label="Certificate Number"
                  name="certificate_number"
                  dependencies={['status']}
                  required={getFieldValue('status') === ComplianceStatus.ACTIVE}
                  rules={[
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (getFieldValue('status') === ComplianceStatus.ACTIVE && !value) {
                          return Promise.reject(new Error('Certificate number is required for Active status'));
                        }
                        return Promise.resolve();
                      },
                    }),
                    { max: 25, message: 'Certificate number must be at most 25 characters' }
                  ]}
                >
                  <Input placeholder="Enter certificate number" maxLength={25} />
                </Form.Item>
              </>
            ) : null
          }
        </Form.Item>

        <Form.Item
          label="Upload Document"
          name="upload"
          dependencies={['doc_type']}
          rules={[
            ({ getFieldValue }) => ({
              validator() {
                const docType = getFieldValue('doc_type');
                if (docType === 'test_report') {
                  const hasExisting = !!record.test_report_filename;
                  if (!uploadFile && !hasExisting) {
                    return Promise.reject(new Error('Test Report document is required'));
                  }
                }
                // Optional for 'certificate' per existing logic (or user didn't specify strictness there)
                // User said "limit certificate number... when selected test report... upload document is required"
                // Implies Upload is strictly required for Test Report.
                return Promise.resolve();
              },
            }),
          ]}
        >
          <Upload
            beforeUpload={(file) => {
              setUploadFile(file);
              // Trigger validation manually defined on the parent Form.Item
              form.validateFields(['upload']);
              return false; // prevent auto upload
            }}
            onRemove={() => {
              setUploadFile(null);
              form.validateFields(['upload']);
            }}
            maxCount={1}
            fileList={uploadFile ? [uploadFile as any] : []}
          >
            <Button icon={<UploadOutlined />}>Select File</Button>
          </Upload>
          <Form.Item noStyle shouldUpdate>
            {({ getFieldValue }) => {
              const type = getFieldValue('doc_type');
              const existing = type === 'test_report' ? record.test_report_filename : record.document_filename;
              return existing ? (
                <div style={{ marginTop: 8 }}>
                  Current {type === 'test_report' ? 'Test Report' : 'Certificate'}: {existing}
                </div>
              ) : null;
            }}
          </Form.Item>
        </Form.Item>

        <Form.Item>
          <Space>
            <Button onClick={() => navigate(-1)}>Cancel</Button>
            <Button type="primary" htmlType="submit" loading={updateMutation.isPending}>
              Save
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
}

export default ComplianceRecordEditPage;


