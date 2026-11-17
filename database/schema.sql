-- NEXUS.GAME - skema database (PostgreSQL). Dibuat otomatis: python -m scripts.export_schema

CREATE TABLE categories (
	id SERIAL NOT NULL, 
	slug VARCHAR(40) NOT NULL, 
	name VARCHAR(60) NOT NULL, 
	hue INTEGER DEFAULT '240' NOT NULL, 
	sort_order INTEGER DEFAULT '0' NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (slug)
);

CREATE TABLE sources (
	id SERIAL NOT NULL, 
	name VARCHAR(80) NOT NULL, 
	feed_url VARCHAR(500) NOT NULL, 
	lang VARCHAR(5) DEFAULT 'en' NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE TABLE articles (
	id SERIAL NOT NULL, 
	slug VARCHAR(120) NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	excerpt VARCHAR(300) DEFAULT '' NOT NULL, 
	body TEXT DEFAULT '' NOT NULL, 
	cover_url VARCHAR(1000), 
	category_id INTEGER NOT NULL, 
	tags VARCHAR(200) DEFAULT '' NOT NULL, 
	author VARCHAR(80) DEFAULT 'Redaksi' NOT NULL, 
	is_featured BOOLEAN DEFAULT false NOT NULL, 
	status VARCHAR(10) DEFAULT 'draft' NOT NULL, 
	views INTEGER DEFAULT '0' NOT NULL, 
	published_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (slug), 
	FOREIGN KEY(category_id) REFERENCES categories (id)
);
CREATE INDEX ix_articles_category_status ON articles (category_id, status);
CREATE INDEX ix_articles_featured ON articles (is_featured);
CREATE INDEX ix_articles_status_published ON articles (status, published_at);
CREATE INDEX ix_articles_views ON articles (views);

CREATE TABLE news (
	id SERIAL NOT NULL, 
	source_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	title VARCHAR(300) NOT NULL, 
	summary VARCHAR(300) DEFAULT '' NOT NULL, 
	image_url VARCHAR(1000), 
	url VARCHAR(1000) NOT NULL, 
	published_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	views INTEGER DEFAULT '0' NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(source_id) REFERENCES sources (id) ON DELETE CASCADE, 
	FOREIGN KEY(category_id) REFERENCES categories (id), 
	UNIQUE (url)
);
CREATE INDEX ix_news_category_published ON news (category_id, published_at);
CREATE INDEX ix_news_published_at ON news (published_at);
CREATE INDEX ix_news_source ON news (source_id);
CREATE INDEX ix_news_views ON news (views);
