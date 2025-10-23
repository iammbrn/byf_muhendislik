-- BYF Mühendislik Veritabanı Indexleri
-- Performans optimizasyonu için gerekli index'ler

--
-- Kullanıcılar tablosu index'leri
--
CREATE INDEX idx_user_user_type ON accounts_customuser(user_type);
CREATE INDEX idx_user_email ON accounts_customuser(email);
CREATE INDEX idx_user_username ON accounts_customuser(username);
CREATE INDEX idx_user_is_active ON accounts_customuser(is_active);
CREATE INDEX idx_user_date_joined ON accounts_customuser(date_joined);
CREATE INDEX idx_user_verification_token ON accounts_customuser(verification_token);

--
-- Firmalar tablosu index'leri
--
CREATE INDEX idx_firm_status ON firms_firm(status);
CREATE INDEX idx_firm_user ON firms_firm(user_id);
CREATE INDEX idx_firm_city ON firms_firm(city);
CREATE INDEX idx_firm_registration_date ON firms_firm(registration_date);
CREATE INDEX idx_firm_contact_person ON firms_firm(contact_person);
CREATE INDEX idx_firm_tax_number ON firms_firm(tax_number);
CREATE INDEX idx_firm_unique_id ON firms_firm(unique_id);

--
-- Hizmetler tablosu index'leri
--
CREATE INDEX idx_service_firm ON services_service(firm_id);
CREATE INDEX idx_service_status ON services_service(status);
CREATE INDEX idx_service_type ON services_service(service_type);
CREATE INDEX idx_service_dates ON services_service(start_date, completion_date);
CREATE INDEX idx_service_request_date ON services_service(request_date);
CREATE INDEX idx_service_assigned_admin ON services_service(assigned_admin_id);
CREATE INDEX idx_service_unique_id ON services_service(unique_id);

--
-- Hizmet talepleri tablosu index'leri
--
CREATE INDEX idx_servicerequest_firm ON services_servicerequest(firm_id);
CREATE INDEX idx_servicerequest_status ON services_servicerequest(status);
CREATE INDEX idx_servicerequest_priority ON services_servicerequest(priority);
CREATE INDEX idx_servicerequest_dates ON services_servicerequest(request_date, updated_at);
CREATE INDEX idx_servicerequest_type ON services_servicerequest(service_type);
CREATE INDEX idx_servicerequest_unique_id ON services_servicerequest(unique_id);

--
-- Dokümanlar tablosu index'leri
--
CREATE INDEX idx_document_firm ON documents_document(firm_id);
CREATE INDEX idx_document_service ON documents_document(service_id);
CREATE INDEX idx_document_type ON documents_document(document_type);
CREATE INDEX idx_document_visible ON documents_document(is_visible_to_firm);
CREATE INDEX idx_document_upload_date ON documents_document(upload_date);
CREATE INDEX idx_document_uploaded_by ON documents_document(uploaded_by_id);
CREATE INDEX idx_document_unique_id ON documents_document(unique_id);

--
-- Blog tablosu index'leri
--
CREATE INDEX idx_blog_status ON blog_post(status);
CREATE INDEX idx_blog_author ON blog_post(author_id);
CREATE INDEX idx_blog_published ON blog_post(published_at);
CREATE INDEX idx_blog_slug ON blog_post(slug);
CREATE INDEX idx_blog_created_at ON blog_post(created_at);
CREATE INDEX idx_blog_views ON blog_post(views);
CREATE INDEX idx_blog_unique_id ON blog_post(unique_id);

--
-- Firma hizmet geçmişi index'leri
--
CREATE INDEX idx_servicehistory_firm ON firms_firmservicehistory(firm_id);
CREATE INDEX idx_servicehistory_dates ON firms_firmservicehistory(service_date, completion_date);
CREATE INDEX idx_servicehistory_type ON firms_firmservicehistory(service_type);

--
-- Full-text search index'leri (Türkçe arama için)
--
CREATE INDEX idx_blog_content_search ON blog_post USING gin(to_tsvector('turkish', content));
CREATE INDEX idx_blog_title_search ON blog_post USING gin(to_tsvector('turkish', title));
CREATE INDEX idx_service_desc_search ON services_service USING gin(to_tsvector('turkish', description));
CREATE INDEX idx_servicerequest_desc_search ON services_servicerequest USING gin(to_tsvector('turkish', description));

--
-- Partial index'ler (Koşullu index'ler)
--
CREATE INDEX idx_active_firms ON firms_firm(status) WHERE status = 'active';
CREATE INDEX idx_published_blog ON blog_post(status, published_at) WHERE status = 'published';
CREATE INDEX idx_visible_documents ON documents_document(is_visible_to_firm) WHERE is_visible_to_firm = true;
CREATE INDEX idx_completed_services ON services_service(status) WHERE status = 'completed';
CREATE INDEX idx_pending_requests ON services_servicerequest(status) WHERE status = 'pending';

--
-- Composite index'ler (Bileşik index'ler)
--
CREATE INDEX idx_firm_services_composite ON services_service(firm_id, status, request_date);
CREATE INDEX idx_user_firm_composite ON accounts_customuser(user_type, is_active, date_joined);
CREATE INDEX idx_document_access_composite ON documents_document(firm_id, is_visible_to_firm, upload_date);