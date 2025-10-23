-- BYF Mühendislik Veritabanı Şeması
-- Ana tablolar ve ilişkiler

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- Kullanıcılar tablosu
--
CREATE TABLE accounts_customuser (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL,
    user_type VARCHAR(10) NOT NULL CHECK (user_type IN ('admin', 'firma')),
    phone VARCHAR(15),
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token UUID DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accounts_customuser IS 'Sistem kullanıcıları tablosu';
COMMENT ON COLUMN accounts_customuser.user_type IS 'Kullanıcı tipi: admin veya firma';

--
-- Firmalar tablosu
--
CREATE TABLE firms_firm (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id INTEGER UNIQUE NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    tax_number VARCHAR(20),
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(254) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) DEFAULT 'Türkiye',
    website VARCHAR(200),
    contact_person VARCHAR(255) NOT NULL,
    contact_person_title VARCHAR(255),
    status VARCHAR(10) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    unique_id UUID DEFAULT uuid_generate_v4() UNIQUE
);

COMMENT ON TABLE firms_firm IS 'Firma bilgileri tablosu';
COMMENT ON COLUMN firms_firm.status IS 'Firma durumu: active, inactive, suspended';

--
-- Hizmetler tablosu
--
CREATE TABLE services_service (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    service_type VARCHAR(50) NOT NULL CHECK (service_type IN (
        'electrical_control', 
        'transformer_consultancy', 
        'electrical_design'
    )),
    description TEXT NOT NULL,
    firm_id INTEGER NOT NULL REFERENCES firms_firm(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'in_progress', 'completed', 'cancelled'
    )),
    request_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    start_date DATE,
    completion_date DATE,
    assigned_admin_id INTEGER REFERENCES accounts_customuser(id) ON DELETE SET NULL,
    unique_id UUID DEFAULT uuid_generate_v4() UNIQUE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE services_service IS 'Hizmet kayıtları tablosu';
COMMENT ON COLUMN services_service.service_type IS 'Hizmet türü: electrical_control, transformer_consultancy, electrical_design';
COMMENT ON COLUMN services_service.status IS 'Hizmet durumu: pending, in_progress, completed, cancelled';

--
-- Hizmet talepleri tablosu
--
CREATE TABLE services_servicerequest (
    id SERIAL PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms_firm(id) ON DELETE CASCADE,
    service_type VARCHAR(50) NOT NULL CHECK (service_type IN (
        'electrical_control', 
        'transformer_consultancy', 
        'electrical_design'
    )),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN (
        'low', 'medium', 'high', 'urgent'
    )),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'in_progress', 'completed', 'cancelled'
    )),
    request_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    unique_id UUID DEFAULT uuid_generate_v4() UNIQUE
);

COMMENT ON TABLE services_servicerequest IS 'Hizmet talepleri tablosu';
COMMENT ON COLUMN services_servicerequest.priority IS 'Talep önceliği: low, medium, high, urgent';

--
-- Dokümanlar tablosu
--
CREATE TABLE documents_document (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN (
        'service_report', 'certificate', 'invoice', 
        'contract', 'technical_drawing', 'other'
    )),
    file VARCHAR(100) NOT NULL,
    firm_id INTEGER NOT NULL REFERENCES firms_firm(id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services_service(id) ON DELETE CASCADE,
    uploaded_by_id INTEGER NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    description TEXT,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    unique_id UUID DEFAULT uuid_generate_v4() UNIQUE,
    is_visible_to_firm BOOLEAN DEFAULT TRUE
);

COMMENT ON TABLE documents_document IS 'Doküman yönetimi tablosu';
COMMENT ON COLUMN documents_document.document_type IS 'Doküman türü: service_report, certificate, invoice, contract, technical_drawing, other';
COMMENT ON COLUMN documents_document.is_visible_to_firm IS 'Firmaya görünürlük durumu';

--
-- Firma hizmet geçmişi
--
CREATE TABLE firms_firmservicehistory (
    id SERIAL PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms_firm(id) ON DELETE CASCADE,
    service_type VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    service_date DATE NOT NULL,
    completion_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

--
-- Blog yazıları
--
CREATE TABLE blog_post (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(300) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    author_id INTEGER NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    featured_image VARCHAR(100),
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE,
    unique_id UUID DEFAULT uuid_generate_v4() UNIQUE
);

COMMENT ON TABLE blog_post IS 'Blog yazıları tablosu';
COMMENT ON COLUMN blog_post.status IS 'Yazı durumu: draft, published, archived';

--
-- Site ayarları
--
CREATE TABLE core_sitesettings (
    id SERIAL PRIMARY KEY,
    site_name VARCHAR(255) DEFAULT 'BYF Mühendislik',
    site_description TEXT,
    contact_email VARCHAR(254),
    contact_phone VARCHAR(15),
    address TEXT,
    logo VARCHAR(100),
    favicon VARCHAR(100),
    facebook_url VARCHAR(200),
    twitter_url VARCHAR(200),
    linkedin_url VARCHAR(200),
    whatsapp_number VARCHAR(20),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE core_sitesettings IS 'Site genel ayarları tablosu';

--
-- Django oturum ve auth tabloları için
--
CREATE TABLE django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL
);

CREATE TABLE django_migrations (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP WITH TIME ZONE NOT NULL
);