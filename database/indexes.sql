-- BYF Mühendislik Veritabanı Indexleri
-- Performans optimizasyonu için gerekli index'ler

--
-- Kullanıcılar tablosu index'leri
--
CREATE INDEX IF NOT EXISTS idx_user_user_type ON accounts_customuser(user_type);
CREATE INDEX IF NOT EXISTS idx_user_email ON accounts_customuser(email);
CREATE INDEX IF NOT EXISTS idx_user_is_active ON accounts_customuser(is_active);
CREATE INDEX IF NOT EXISTS idx_user_date_joined ON accounts_customuser(date_joined);

--
-- Firmalar tablosu index'leri
--
CREATE INDEX IF NOT EXISTS idx_firm_status ON firms_firm(status);
CREATE INDEX IF NOT EXISTS idx_firm_city ON firms_firm(city);
CREATE INDEX IF NOT EXISTS idx_firm_registration_date ON firms_firm(registration_date);

--
-- Hizmetler tablosu index'leri
--
CREATE INDEX IF NOT EXISTS idx_service_firm ON services_service(firm_id);
CREATE INDEX IF NOT EXISTS idx_service_status ON services_service(status);
CREATE INDEX IF NOT EXISTS idx_service_type ON services_service(service_type);
CREATE INDEX IF NOT EXISTS idx_service_request_date ON services_service(request_date);
CREATE INDEX IF NOT EXISTS idx_service_assigned_admin ON services_service(assigned_admin_id);

--
-- Hizmet talepleri tablosu index'leri
--
CREATE INDEX IF NOT EXISTS idx_servicerequest_firm ON services_servicerequest(firm_id);
CREATE INDEX IF NOT EXISTS idx_servicerequest_status ON services_servicerequest(status);
CREATE INDEX IF NOT EXISTS idx_servicerequest_priority ON services_servicerequest(priority);
CREATE INDEX IF NOT EXISTS idx_servicerequest_type ON services_servicerequest(service_type);
CREATE INDEX IF NOT EXISTS idx_servicerequest_tracking_code ON services_servicerequest(tracking_code);
CREATE INDEX IF NOT EXISTS idx_servicerequest_responded_by ON services_servicerequest(responded_by_id);

--
-- Dokümanlar tablosu index'leri
--
CREATE INDEX IF NOT EXISTS idx_document_firm ON documents_document(firm_id);
CREATE INDEX IF NOT EXISTS idx_document_service ON documents_document(service_id);
CREATE INDEX IF NOT EXISTS idx_document_type ON documents_document(document_type);
CREATE INDEX IF NOT EXISTS idx_document_visible ON documents_document(is_visible_to_firm);
CREATE INDEX IF NOT EXISTS idx_document_upload_date ON documents_document(upload_date);
CREATE INDEX IF NOT EXISTS idx_document_parent ON documents_document(parent_id);

--
-- Blog tablosu
--
CREATE INDEX IF NOT EXISTS idx_blog_status ON blog_blogpost(status);
CREATE INDEX IF NOT EXISTS idx_blog_published ON blog_blogpost(published_at);
CREATE INDEX IF NOT EXISTS idx_blog_slug ON blog_blogpost(slug);

--
-- Full-text search
--
CREATE INDEX IF NOT EXISTS idx_blog_content_search ON blog_blogpost USING gin(to_tsvector('turkish', content));
CREATE INDEX IF NOT EXISTS idx_blog_title_search ON blog_blogpost USING gin(to_tsvector('turkish', title));

--
-- Partial indexes
--
CREATE INDEX IF NOT EXISTS idx_active_firms ON firms_firm(status) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_published_blog ON blog_blogpost(status, published_at) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS idx_visible_documents ON documents_document(is_visible_to_firm) WHERE is_visible_to_firm = true;
CREATE INDEX IF NOT EXISTS idx_pending_requests ON services_servicerequest(status) WHERE status = 'pending';

--
-- Composite indexes
--
CREATE INDEX IF NOT EXISTS idx_firm_services_composite ON services_service(firm_id, status, request_date);
CREATE INDEX IF NOT EXISTS idx_document_access_composite ON documents_document(firm_id, is_visible_to_firm, upload_date);