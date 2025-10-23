-- BYF Mühendislik Veritabanı Şeması
-- Ana tablolar ve ilişkiler

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- Kullanıcılar tablosu
CREATE TABLE IF NOT EXISTS accounts_customuser (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_type VARCHAR(10) NOT NULL DEFAULT 'firma' CHECK (user_type IN ('admin', 'firma')),
    phone VARCHAR(15) DEFAULT '',
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token UUID DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accounts_customuser IS 'Sistem kullanıcıları tablosu';

-- Firmalar tablosu
CREATE TABLE IF NOT EXISTS firms_firm (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id INTEGER UNIQUE REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    tax_number VARCHAR(20) DEFAULT '',
    phone VARCHAR(15) DEFAULT '',
    email VARCHAR(254) DEFAULT '',
    address TEXT DEFAULT '',
    city VARCHAR(100) DEFAULT '',
    country VARCHAR(100) DEFAULT 'Türkiye',
    website VARCHAR(200) DEFAULT '',
    contact_person VARCHAR(255) DEFAULT '',
    contact_person_title VARCHAR(255) DEFAULT '',
    status VARCHAR(10) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    unique_id UUID DEFAULT uuid_generate_v4() UNIQUE
);

COMMENT ON TABLE firms_firm IS 'Firma bilgileri tablosu';

-- Hizmetler tablosu
CREATE TABLE IF NOT EXISTS services_service (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('electrical_control', 'transformer_consultancy', 'electrical_design')),
    description TEXT NOT NULL,
    firm_id INTEGER NOT NULL REFERENCES firms_firm(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    request_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    start_date DATE,
    completion_date DATE,
    assigned_admin_id INTEGER REFERENCES accounts_customuser(id) ON DELETE SET NULL,
    unique_id UUID DEFAULT uuid_generate_v4() UNIQUE,
    notes TEXT DEFAULT ''
);

COMMENT ON TABLE services_service IS 'Hizmet kayıtları tablosu';

-- Hizmet talepleri tablosu
CREATE TABLE IF NOT EXISTS services_servicerequest (
    id SERIAL PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms_firm(id) ON DELETE CASCADE,
    service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('electrical_control', 'transformer_consultancy', 'electrical_design')),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled', 'in_progress', 'completed')),
    request_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    unique_id UUID DEFAULT uuid_generate_v4() UNIQUE,
    tracking_code VARCHAR(20) UNIQUE,
    requested_completion_date DATE,
    admin_response TEXT DEFAULT '',
    responded_by_id INTEGER REFERENCES accounts_customuser(id) ON DELETE SET NULL
);

COMMENT ON TABLE services_servicerequest IS 'Hizmet talepleri tablosu';

-- Dokümanlar tablosu
CREATE TABLE IF NOT EXISTS documents_document (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN ('service_report', 'certificate', 'invoice', 'contract', 'technical_drawing', 'other')),
    file VARCHAR(100) NOT NULL,
    firm_id INTEGER NOT NULL REFERENCES firms_firm(id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services_service(id) ON DELETE CASCADE,
    uploaded_by_id INTEGER NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    description TEXT DEFAULT '',
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    unique_id UUID DEFAULT uuid_generate_v4() UNIQUE,
    is_visible_to_firm BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    parent_id INTEGER REFERENCES documents_document(id) ON DELETE SET NULL,
    download_count INTEGER DEFAULT 0
);

COMMENT ON TABLE documents_document IS 'Doküman yönetimi tablosu';

-- Blog yazıları
CREATE TABLE IF NOT EXISTS blog_blogpost (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(300) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT DEFAULT '',
    author_id INTEGER NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    category VARCHAR(32) DEFAULT 'general',
    featured_image VARCHAR(100) DEFAULT '',
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE,
    unique_id UUID DEFAULT uuid_generate_v4() UNIQUE
);

COMMENT ON TABLE blog_blogpost IS 'Blog yazıları tablosu';

-- Site ayarları
CREATE TABLE IF NOT EXISTS core_sitesettings (
    id SERIAL PRIMARY KEY,
    site_name VARCHAR(255) DEFAULT 'BYF Mühendislik',
    site_description TEXT DEFAULT '',
    contact_email VARCHAR(254) DEFAULT '',
    contact_phone VARCHAR(15) DEFAULT '',
    address TEXT DEFAULT '',
    logo VARCHAR(100) DEFAULT '',
    favicon VARCHAR(100) DEFAULT '',
    hero_image VARCHAR(100) DEFAULT '',
    about_image VARCHAR(100) DEFAULT '',
    facebook_url VARCHAR(200) DEFAULT '',
    twitter_url VARCHAR(200) DEFAULT '',
    linkedin_url VARCHAR(200) DEFAULT '',
    instagram_url VARCHAR(200) DEFAULT '',
    whatsapp_number VARCHAR(20) DEFAULT '',
    google_analytics_id VARCHAR(32) DEFAULT '',
    hotjar_id VARCHAR(20) DEFAULT '',
    google_search_console VARCHAR(100) DEFAULT '',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE core_sitesettings IS 'Site genel ayarları tablosu';

-- Activity Log
CREATE TABLE IF NOT EXISTS core_activitylog (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES accounts_customuser(id) ON DELETE SET NULL,
    action VARCHAR(16) NOT NULL CHECK (action IN ('login', 'logout', 'create', 'update', 'delete')),
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE core_activitylog IS 'Kullanıcı aktivite logları';

-- Provisioned Credentials
CREATE TABLE IF NOT EXISTS core_provisionedcredential (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES accounts_customuser(id) ON DELETE CASCADE,
    username VARCHAR(150) NOT NULL,
    password_plain VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Contact Messages
CREATE TABLE IF NOT EXISTS core_contactmessage (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(254) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'new' CHECK (status IN ('new', 'read', 'replied', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP WITH TIME ZONE,
    response_note TEXT DEFAULT ''
);

COMMENT ON TABLE core_contactmessage IS 'İletişim formu mesajları';

-- Service Categories
CREATE TABLE IF NOT EXISTS core_servicecategory (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    icon VARCHAR(50) DEFAULT 'fa-cogs',
    subtitle VARCHAR(300) NOT NULL,
    description TEXT NOT NULL,
    scope_items TEXT NOT NULL,
    features TEXT NOT NULL,
    process_steps JSONB,
    standards TEXT DEFAULT '',
    "order" INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE core_servicecategory IS 'Hizmet kategorileri';

-- Team Members
CREATE TABLE IF NOT EXISTS core_teammember (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    bio TEXT NOT NULL,
    image VARCHAR(100) NOT NULL,
    email VARCHAR(254) DEFAULT '',
    phone VARCHAR(20) DEFAULT '',
    linkedin_url VARCHAR(200) DEFAULT '',
    "order" INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE core_teammember IS 'Ekip üyeleri';
