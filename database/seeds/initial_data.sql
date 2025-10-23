-- BYF Mühendislik Başlangıç Verileri
-- Sistemin çalışması için gerekli temel veriler

--
-- Site ayarları
--
INSERT INTO core_sitesettings (
    site_name, 
    site_description, 
    contact_email, 
    contact_phone, 
    address, 
    facebook_url, 
    twitter_url, 
    linkedin_url, 
    whatsapp_number
) VALUES (
    'BYF Mühendislik',
    'Elektriksel periyodik kontrol hizmeti ve Trafo müşavirlik konularında hizmet veren kuruluş. Profesyonel mühendislik çözümleri ile sektörde lider.',
    'info@byfmuhendislik.com',
    '+90 212 555 01 01',
    'Prof. Dr. Bülent Tarcan Sk. No:12, 34349 Beşiktaş/İstanbul',
    'https://facebook.com/byfmuhendislik',
    'https://twitter.com/byfmuhendislik',
    'https://linkedin.com/company/byfmuhendislik',
    '+90 555 012 34 56'
);

--
-- Örnek admin kullanıcısı (şifre: admin123 - hashlenmiş olarak)
--
INSERT INTO accounts_customuser (
    password, 
    username, 
    first_name, 
    last_name, 
    email, 
    is_staff, 
    is_superuser, 
    is_active, 
    date_joined, 
    user_type,
    phone
) VALUES (
    'pbkdf2_sha256$600000$xyz123abc456$hashedpasswordhere=', -- Gerçek hash Django tarafından oluşturulacak
    'admin',
    'Sistem',
    'Yöneticisi',
    'admin@byfmuhendislik.com',
    true,
    true,
    true,
    CURRENT_TIMESTAMP,
    'admin',
    '+90 555 012 34 57'
);

--
-- Örnek firma kullanıcıları
--
INSERT INTO accounts_customuser (
    password, 
    username, 
    first_name, 
    last_name, 
    email, 
    is_staff, 
    is_superuser, 
    is_active, 
    date_joined, 
    user_type,
    phone
) VALUES 
(
    'pbkdf2_sha256$600000$def789ghi012$hashedpassword1=', -- şifre: firma123
    'firma_abc',
    'Ahmet',
    'Yılmaz',
    'ahmet@abcmadencilik.com',
    false,
    false,
    true,
    CURRENT_TIMESTAMP,
    'firma',
    '+90 532 111 22 33'
),
(
    'pbkdf2_sha256$600000$jkl345mno678$hashedpassword2=', -- şifre: firma123
    'firma_xyz',
    'Mehmet',
    'Kaya',
    'mehmet@xyzinşaat.com',
    false,
    false,
    true,
    CURRENT_TIMESTAMP,
    'firma',
    '+90 533 444 55 66'
);

--
-- Örnek firmalar
--
INSERT INTO firms_firm (
    name,
    user_id,
    tax_number,
    phone,
    email,
    address,
    city,
    contact_person,
    contact_person_title,
    status
) VALUES 
(
    'ABC Madencilik A.Ş.',
    (SELECT id FROM accounts_customuser WHERE username = 'firma_abc'),
    '1234567890',
    '+90 212 444 01 01',
    'info@abcmadencilik.com',
    'Organize Sanayi Bölgesi 1. Cadde No:15, 34500 Beylikdüzü/İstanbul',
    'İstanbul',
    'Ahmet Yılmaz',
    'Genel Müdür',
    'active'
),
(
    'XYZ İnşaat Ltd. Şti.',
    (SELECT id FROM accounts_customuser WHERE username = 'firma_xyz'),
    '0987654321',
    '+90 216 333 02 02',
    'info@xyzinşaat.com',
    'Maslak Mah. Büyükdere Cad. No:245, 34398 Sarıyer/İstanbul',
    'İstanbul',
    'Mehmet Kaya',
    'Proje Müdürü',
    'active'
);

--
-- Örnek hizmetler
--
INSERT INTO services_service (
    name,
    service_type,
    description,
    firm_id,
    status,
    request_date,
    start_date,
    completion_date,
    assigned_admin_id,
    notes
) VALUES 
(
    'Yıllık Elektriksel Periyodik Kontrol',
    'electrical_control',
    'Tesisin yıllık elektriksel periyodik kontrolü ve ölçümleri. Topraklama, kaçak akım ve yalıtım direnci testleri yapıldı.',
    (SELECT id FROM firms_firm WHERE name = 'ABC Madencilik A.Ş.'),
    'completed',
    '2024-01-10 09:00:00',
    '2024-01-15',
    '2024-01-20',
    (SELECT id FROM accounts_customuser WHERE username = 'admin'),
    'Tüm testler başarıyla tamamlandı. Rapor hazırlandı.'
),
(
    'Trafo Merkezi Danışmanlık Hizmeti',
    'transformer_consultancy',
    'Yeni trafo merkezi kurulumu için danışmanlık ve proje yönetimi hizmeti.',
    (SELECT id FROM firms_firm WHERE name = 'XYZ İnşaat Ltd. Şti.'),
    'in_progress',
    '2024-01-12 14:30:00',
    '2024-01-18',
    NULL,
    (SELECT id FROM accounts_customuser WHERE username = 'admin'),
    'Proje devam ediyor. Haftalık toplantılar yapılıyor.'
);

--
-- Örnek hizmet talepleri
--
INSERT INTO services_servicerequest (
    firm_id,
    service_type,
    title,
    description,
    priority,
    status
) VALUES 
(
    (SELECT id FROM firms_firm WHERE name = 'ABC Madencilik A.Ş.'),
    'electrical_design',
    'Yeni Tesis Elektrik Projesi',
    'Yeni üretim tesisimiz için elektrik projesi çizimi ve onay süreçleri için destek talep ediyoruz.',
    'high',
    'pending'
),
(
    (SELECT id FROM firms_firm WHERE name = 'XYZ İnşaat Ltd. Şti.'),
    'transformer_consultancy',
    'Trafo Kapasite Artışı',
    'Mevcut trafo merkezimizin kapasite artışı için danışmanlık hizmeti talep ediyoruz.',
    'medium',
    'pending'
);

--
-- Örnek blog yazıları
--
INSERT INTO blog_post (
    title,
    slug,
    content,
    excerpt,
    author_id,
    status,
    published_at,
    views
) VALUES 
(
    'Elektriksel Periyodik Kontrolün Önemi',
    'elektriksel-periyodik-kontrolun-onemi',
    '<p>Elektriksel periyodik kontrol, işletmelerin elektrik tesisatlarının güvenli ve verimli çalışmasını sağlamak için hayati öneme sahiptir. Bu kontroller sayesinde:</p>
    <ul>
        <li>Elektrik kaynaklı yangın riski azaltılır</li>
        <li>Enerji verimliliği artırılır</li>
        <li>İş güvenliği mevzuatına uyum sağlanır</li>
        <li>Ekipman ömrü uzatılır</li>
    </ul>
    <p>Düzenli periyodik kontroller ile olası arızalar önceden tespit edilerek büyük maliyetlerden kaçınılabilir.</p>',
    'Elektriksel periyodik kontrolün işletmeler için önemi ve düzenli kontrollerin sağladığı faydalar hakkında detaylı bilgi.',
    (SELECT id FROM accounts_customuser WHERE username = 'admin'),
    'published',
    '2024-01-01 10:00:00',
    156
),
(
    'Trafo Müşavirliği Hizmetleri ve Faydaları',
    'trafo-musavirligi-hizmetleri-ve-faydalari',
    '<p>Trafo müşavirliği hizmetleri, enerji dağıtım sistemlerinin verimli ve güvenli çalışmasını sağlamak için kritik öneme sahiptir. Bu hizmetler kapsamında:</p>
    <h3>Hizmet Alanlarımız:</h3>
    <ul>
        <li>Trafo proje danışmanlığı</li>
        <li>İşletme ve bakım süreçleri</li>
        <li>Periyodik test ve ölçümler</li>
        <li>Arıza analizi ve çözüm önerileri</li>
    </ul>
    <p>Profesyonel trafo müşavirliği hizmeti ile enerji kesintilerini minimize edebilir, bakım maliyetlerinizi düşürebilirsiniz.</p>',
    'Trafo müşavirliği hizmetlerinin kapsamı ve işletmelere sağladığı avantajlar hakkında bilgilendirme.',
    (SELECT id FROM accounts_customuser WHERE username = 'admin'),
    'published',
    '2024-01-05 14:30:00',
    89
);