/**
 * TypeScript Type Definitions
 * ============================
 * Defines all data models matching the backend API responses.
 */

/**
 * Compliance Status Enum
 */
export enum ComplianceStatus {
  PENDING = 'PENDING',
  ACTIVE = 'ACTIVE',
  EXPIRING = 'EXPIRING',
  EXPIRED = 'EXPIRED',
}

export enum LabelingStatus {
  PENDING = 'PENDING',
  DONE = 'DONE',
}

/**
 * Technology Model
 */
export interface Technology {
  id: number;
  name: string;
  description?: string;
  created_at: string;
}

/**
 * Country Model
 */
export interface Country {
  id: number;
  name: string;
  iso_code: string;
  created_at: string;
  details?: Record<string, any>;
}

/**
 * Certification Model
 */
export interface Certification {
  id: number;
  name: string;
  authority_name?: string;
  description?: string;
  created_at: string;
}

/**
 * Certification Label Model
 */
export interface CertificationLabel {
  id: number;
  name: string;
  authority: string;
  description?: string;
  image_url?: string;
  vector_url?: string;
  country_id?: number | null;
  requirements?: {
    region?: string;
    min_height?: string;
    placement?: string;
    content?: string;
    [key: string]: any;
  };
}

/**
 * Regulatory Matrix Rule Model
 */
export interface RegulatoryRule {
  id: number;
  technology_id: number;
  country_id: number;
  certification_id: number;
  is_mandatory: boolean;
  notes?: string;
  created_at: string;
  technology_name?: string;
  country_name?: string;
  certification_name?: string;
}

/**
 * Tenant Model
 */
export interface Tenant {
  id: string; // UUID
  name: string;
  contact_email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Notification Rule Model
 */
export interface NotificationRule {
  id: number;
  tenant_id: string;
  days_before_expiry: number;
  severity_level: string;
  is_active: boolean;
  created_at: string;
}

/**
 * Device Model
 */
export interface Device {
  id: string; // UUID
  tenant_id: string;
  model_name: string;
  sku?: string;
  description?: string;
  created_at: string;
  updated_at: string;
  technologies?: Technology[];
  target_countries?: string[];
}

/**
 * Compliance Record Model
 */
export interface ComplianceRecord {
  id: string; // UUID
  tenant_id: string;
  device_id: string;
  country_id: number;
  certification_id: number;
  status: ComplianceStatus;
  labeling_status?: LabelingStatus;
  labeling_updated_at?: string;
  expiry_date?: string;
  certificate_number?: string;
  document_path?: string;
  document_filename?: string;
  document_mime_type?: string;
  test_report_path?: string;
  test_report_filename?: string;
  test_report_mime_type?: string;
  labeling_picture_path?: string;
  labeling_picture_filename?: string;
  labeling_picture_mime_type?: string;
  last_notified_at?: string;
  created_at: string;
  updated_at: string;
  device_name?: string;
  country_name?: string;
  certification_name?: string;
  task_progress_percent?: number;
  task_counts?: {
    total?: number;
    done?: number;
    in_progress?: number;
    pending?: number;
  };
}

/**
 * Gap Analysis Request
 */
export interface GapAnalysisRequest {
  device_id: string;
  country_id: number;
}

/**
 * Gap Analysis Result Item
 */
export interface GapAnalysisResultItem {
  certification_id: number;
  certification_name: string;
  technology: string;
  has_gap: boolean;
  status?: string;
  expiry_date?: string;
  compliance_record_id?: string;
  branding_image_url?: string;
  labeling_requirements?: string;
  open_tasks_count?: number;
}

/**
 * Gap Analysis Response
 */
export interface GapAnalysisResponse {
  device_id: string;
  country_id: number;
  total_required: number;
  gaps_found: number;
  results: GapAnalysisResultItem[];
}

/**
 * Compliance Task Models
 */
export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'DONE';

export interface ComplianceTask {
  id: string;
  record_id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  assignee?: string;
  created_by?: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
}

export interface ComplianceTaskNote {
  id: string;
  task_id: string;
  note: string;
  author?: string;
  created_at: string;
}

export interface GlossaryTable {
  headers: string[];
  rows: string[][];
  title?: string;
}

export interface GlossarySection {
  title?: string;
  content?: string[];
  table?: GlossaryTable;
  listItems?: string[];
  images?: string[]; // URLs of images in this section
}

export interface GlossaryArticle {
  id: string;
  term: string;
  category: 'General' | 'Radio' | 'EMC' | 'Safety' | 'Regulatory' | 'Japan';
  region?: string;
  summary: string;
  sections: GlossarySection[];
}


