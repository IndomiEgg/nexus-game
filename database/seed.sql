-- Data awal. Aman dijalankan berulang (ON CONFLICT DO NOTHING).
INSERT INTO categories (slug, name, hue, sort_order) VALUES ('pc', 'PC', 260, 1) ON CONFLICT (slug) DO NOTHING;
INSERT INTO categories (slug, name, hue, sort_order) VALUES ('console', 'Console', 200, 2) ON CONFLICT (slug) DO NOTHING;
INSERT INTO categories (slug, name, hue, sort_order) VALUES ('mobile', 'Mobile', 150, 3) ON CONFLICT (slug) DO NOTHING;
INSERT INTO categories (slug, name, hue, sort_order) VALUES ('esports', 'Esports', 330, 4) ON CONFLICT (slug) DO NOTHING;
INSERT INTO categories (slug, name, hue, sort_order) VALUES ('review', 'Review', 30, 5) ON CONFLICT (slug) DO NOTHING;
INSERT INTO categories (slug, name, hue, sort_order) VALUES ('industry', 'Industry', 45, 6) ON CONFLICT (slug) DO NOTHING;
INSERT INTO categories (slug, name, hue, sort_order) VALUES ('indie', 'Indie', 100, 7) ON CONFLICT (slug) DO NOTHING;
INSERT INTO categories (slug, name, hue, sort_order) VALUES ('general', 'General', 240, 8) ON CONFLICT (slug) DO NOTHING;

INSERT INTO articles (slug, title, excerpt, body, category_id, tags, author, is_featured, status, published_at)
VALUES ('panduan-merakit-pc-gaming-hemat', 'Panduan Merakit PC Gaming Hemat di 2026',
 'Merakit PC gaming tidak harus mahal. Kuncinya ada pada prioritas komponen.',
 '<p>Merakit PC gaming tidak harus mahal. Kuncinya ada pada <strong>prioritas komponen</strong>.</p><h2>Utamakan GPU</h2><p>Sebagian besar budget sebaiknya masuk ke kartu grafis, karena itu yang paling menentukan FPS.</p><h2>Jangan abaikan PSU</h2><p>Power supply murah yang tidak jelas mereknya berisiko merusak komponen lain.</p>',
 (SELECT id FROM categories WHERE slug = 'pc'), 'pc,rakit,budget', 'Redaksi', TRUE, 'published', '2026-11-16 08:00:00')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO articles (slug, title, excerpt, body, category_id, tags, author, is_featured, status, published_at)
VALUES ('game-indie-wajib-coba-bulan-ini', '5 Game Indie yang Wajib Kamu Coba Bulan Ini',
 'Game indie sering menawarkan ide yang lebih berani dibanding game AAA.',
 '<p>Game indie sering menawarkan ide yang lebih berani dibanding game AAA. Cara memilih yang layak dibeli:</p><ul><li>Cek ulasan pemain di Steam</li><li>Tonton gameplay singkat</li><li>Coba demo bila tersedia</li></ul>',
 (SELECT id FROM categories WHERE slug = 'indie'), 'indie,rekomendasi', 'Redaksi', FALSE, 'published', '2026-11-15 08:00:00')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO articles (slug, title, excerpt, body, category_id, tags, author, is_featured, status, published_at)
VALUES ('opini-masa-depan-esports-indonesia', 'Opini - Masa Depan Esports Indonesia',
 'Esports Indonesia terus tumbuh, tetapi ekosistemnya masih butuh pembinaan dari akar rumput.',
 '<p>Esports Indonesia terus tumbuh, tetapi <strong>ekosistemnya</strong> masih butuh pembinaan dari level akar rumput.</p><blockquote>Turnamen besar penting, tetapi liga kampus dan komunitas adalah fondasinya.</blockquote>',
 (SELECT id FROM categories WHERE slug = 'esports'), 'esports,opini', 'Redaksi', FALSE, 'published', '2026-11-14 08:00:00')
ON CONFLICT (slug) DO NOTHING;
