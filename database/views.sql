-- BYF Mühendislik Veritabanı View'ları
-- Raporlama ve dashboard verileri için

--
-- Dashboard istatistikleri view'ı
--
CREATE OR REPLACE VIEW dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM firms_firm WHERE status = 'active') as active_firms,
    (SELECT COUNT(*) FROM services_service WHERE status = 'in_progress') as active_services,
    (SELECT COUNT(*) FROM services_servicerequest WHERE status = 'pending') as pending_requests,
    (SELECT COUNT(*) FROM services_service WHERE status = 'completed' 
     AND completion_date >= CURRENT_DATE - INTERVAL '30 days') as completed_this_month,
    (SELECT COUNT(*) FROM documents_document 
     WHERE upload_date >= CURRENT_DATE - INTERVAL '7 days') as documents_this_week,
    (SELECT COUNT(*) FROM blog_post WHERE status = 'published') as published_posts;

--
-- Firma dashboard view'ı
--
CREATE OR REPLACE VIEW firm_dashboard_data AS
SELECT 
    f.id as firm_id,
    f.name as firm_name,
    f.contact_person,
    COUNT(DISTINCT s.id) as total_services,
    COUNT(DISTINCT sr.id) as total_requests,
    COUNT(DISTINCT d.id) as total_documents,
    COUNT(DISTINCT CASE WHEN s.status = 'completed' THEN s.id END) as completed_services,
    COUNT(DISTINCT CASE WHEN s.status = 'in_progress' THEN s.id END) as in_progress_services,
    MAX(s.completion_date) as last_service_date,
    f.registration_date
FROM firms_firm f
LEFT JOIN services_service s ON f.id = s.firm_id
LEFT JOIN services_servicerequest sr ON f.id = sr.firm_id
LEFT JOIN documents_document d ON f.id = d.firm_id AND d.is_visible_to_firm = true
GROUP BY f.id, f.name, f.contact_person, f.registration_date;

--
-- Hizmet raporlama view'ı
--
CREATE OR REPLACE VIEW service_reports AS
SELECT 
    s.id,
    s.name as service_name,
    s.service_type,
    s.status,
    s.request_date,
    s.start_date,
    s.completion_date,
    f.name as firm_name,
    f.contact_person,
    f.phone as firm_phone,
    f.email as firm_email,
    u.username as assigned_admin,
    COUNT(d.id) as document_count,
    CASE 
        WHEN s.completion_date IS NOT NULL THEN 
            EXTRACT(DAY FROM (s.completion_date - s.start_date))
        ELSE 
            EXTRACT(DAY FROM (CURRENT_DATE - s.start_date))
    END as duration_days
FROM services_service s
JOIN firms_firm f ON s.firm_id = f.id
LEFT JOIN accounts_customuser u ON s.assigned_admin_id = u.id
LEFT JOIN documents_document d ON s.id = d.service_id
GROUP BY s.id, s.name, s.service_type, s.status, s.request_date, s.start_date, 
         s.completion_date, f.name, f.contact_person, f.phone, f.email, u.username;

--
-- Doküman envanter view'ı
--
CREATE OR REPLACE VIEW document_inventory AS
SELECT 
    d.id,
    d.name as document_name,
    d.document_type,
    d.upload_date,
    f.name as firm_name,
    s.name as service_name,
    u.username as uploaded_by,
    d.is_visible_to_firm,
    CASE 
        WHEN d.file LIKE '%.pdf' THEN 'PDF'
        WHEN d.file LIKE '%.doc%' THEN 'Word'
        WHEN d.file LIKE '%.xls%' THEN 'Excel'
        WHEN d.file LIKE '%.jpg%' OR d.file LIKE '%.png%' THEN 'Image'
        ELSE 'Other'
    END as file_type
FROM documents_document d
JOIN firms_firm f ON d.firm_id = f.id
LEFT JOIN services_service s ON d.service_id = s.id
JOIN accounts_customuser u ON d.uploaded_by_id = u.id;

--
-- Aylık hizmet istatistikleri view'ı
--
CREATE OR REPLACE VIEW monthly_service_stats AS
SELECT 
    DATE_TRUNC('month', request_date) as month,
    service_type,
    COUNT(*) as total_requests,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
    ROUND(AVG(
        CASE 
            WHEN completion_date IS NOT NULL THEN 
                EXTRACT(DAY FROM (completion_date - start_date))
        END
    ), 2) as avg_completion_days
FROM services_service
GROUP BY DATE_TRUNC('month', request_date), service_type
ORDER BY month DESC, service_type;

--
-- Firma aktivite view'ı
--
CREATE OR REPLACE VIEW firm_activity AS
SELECT 
    f.id as firm_id,
    f.name as firm_name,
    f.registration_date,
    MAX(s.request_date) as last_service_request,
    MAX(sr.request_date) as last_service_created,
    MAX(d.upload_date) as last_document_upload,
    COUNT(DISTINCT s.id) as total_services,
    COUNT(DISTINCT sr.id) as total_requests,
    COUNT(DISTINCT d.id) as total_documents
FROM firms_firm f
LEFT JOIN services_service s ON f.id = s.firm_id
LEFT JOIN services_servicerequest sr ON f.id = sr.firm_id
LEFT JOIN documents_document d ON f.id = d.firm_id
GROUP BY f.id, f.name, f.registration_date;