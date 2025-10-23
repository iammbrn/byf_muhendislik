-- BYF Mühendislik Veritabanı Tetikleyicileri
-- Otomatik güncellemeler ve iş kuralları için

--
-- Otomatik timestamp güncelleme fonksiyonu
--
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

--
-- Kullanıcı updated_at tetikleyicisi
--
CREATE TRIGGER update_accounts_user_updated_at 
    BEFORE UPDATE ON accounts_customuser 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

--
-- Firma updated_at tetikleyicisi
--
CREATE TRIGGER update_firm_updated_at 
    BEFORE UPDATE ON firms_firm 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

--
-- Hizmet talebi updated_at tetikleyicisi
--
CREATE TRIGGER update_service_request_updated_at 
    BEFORE UPDATE ON services_servicerequest 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

--
-- Blog updated_at tetikleyicisi
--
CREATE TRIGGER update_blog_updated_at 
    BEFORE UPDATE ON blog_post 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

--
-- Site ayarları updated_at tetikleyicisi
--
CREATE TRIGGER update_sitesettings_updated_at 
    BEFORE UPDATE ON core_sitesettings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

--
-- Hizmet tamamlandığında otomatik geçmiş kaydı oluşturma
--
CREATE OR REPLACE FUNCTION create_service_history()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        INSERT INTO firms_firmservicehistory 
        (firm_id, service_type, description, service_date, completion_date)
        VALUES (
            NEW.firm_id, 
            (SELECT name FROM services_service WHERE id = NEW.id),
            NEW.description,
            COALESCE(NEW.start_date, CURRENT_DATE),
            COALESCE(NEW.completion_date, CURRENT_DATE)
        );
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER service_completed_history 
    AFTER UPDATE ON services_service 
    FOR EACH ROW EXECUTE FUNCTION create_service_history();

--
-- Blog yayınlandığında published_at otomatik ayarlama
--
CREATE OR REPLACE FUNCTION set_blog_published_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'published' AND OLD.status != 'published' THEN
        NEW.published_at = CURRENT_TIMESTAMP;
    ELSIF NEW.status != 'published' THEN
        NEW.published_at = NULL;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER set_blog_published_date 
    BEFORE UPDATE ON blog_post 
    FOR EACH ROW EXECUTE FUNCTION set_blog_published_at();

--
-- Firma oluşturulduğunda kullanıcı tipini kontrol et
--
CREATE OR REPLACE FUNCTION check_firm_user_type()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT user_type FROM accounts_customuser WHERE id = NEW.user_id) != 'firma' THEN
        RAISE EXCEPTION 'Sadece firma tipindeki kullanıcılar için firma kaydı oluşturulabilir';
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER enforce_firm_user_type 
    BEFORE INSERT ON firms_firm 
    FOR EACH ROW EXECUTE FUNCTION check_firm_user_type();

--
-- Doküman yükleme tarihi kontrolü
--
CREATE OR REPLACE FUNCTION set_document_upload_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.upload_date IS NULL THEN
        NEW.upload_date = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER set_document_upload_date 
    BEFORE INSERT ON documents_document 
    FOR EACH ROW EXECUTE FUNCTION set_document_upload_date();