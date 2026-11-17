-- =====================================================================
-- Nike (NKE) Karar Destek Sistemi - MySQL Veritabanı
-- ER Diyagramı ve Akış Şemasına göre hazırlanmıştır.
-- =====================================================================

DROP DATABASE IF EXISTS nke_dss;
CREATE DATABASE nke_dss CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nke_dss;

-- ---------------------------------------------------------------------
-- 1) COMPANY
-- ---------------------------------------------------------------------
CREATE TABLE COMPANY (
    company_id     INT AUTO_INCREMENT PRIMARY KEY,
    company_name   VARCHAR(100) NOT NULL,
    ticker_symbol  VARCHAR(10)  NOT NULL UNIQUE,
    sector         VARCHAR(50),
    market         VARCHAR(50)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2) STOCK_PRICE  (COMPANY 1:N STOCK_PRICE)
-- ---------------------------------------------------------------------
CREATE TABLE STOCK_PRICE (
    price_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    company_id   INT NOT NULL,
    price_date   DATE NOT NULL,
    open_price   DECIMAL(12,4),
    high_price   DECIMAL(12,4),
    low_price    DECIMAL(12,4),
    close_price  DECIMAL(12,4),
    volume       BIGINT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_company_date (company_id, price_date),
    CONSTRAINT fk_stock_company
        FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3) KPI_TYPE
-- ---------------------------------------------------------------------
CREATE TABLE KPI_TYPE (
    kpi_type_id  INT AUTO_INCREMENT PRIMARY KEY,
    kpi_name     VARCHAR(50) NOT NULL UNIQUE,
    description  TEXT,
    formula_text TEXT,
    unit         VARCHAR(20),
    is_active    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 4) KPI_VALUE  (STOCK_PRICE 1:N KPI_VALUE, KPI_TYPE 1:N KPI_VALUE)
-- ---------------------------------------------------------------------
CREATE TABLE KPI_VALUE (
    kpi_value_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    price_id         BIGINT NOT NULL,
    kpi_type_id      INT NOT NULL,
    kpi_value        DECIMAL(18,6),
    calculation_date DATE,
    period_info      VARCHAR(30),
    CONSTRAINT fk_kpival_price
        FOREIGN KEY (price_id) REFERENCES STOCK_PRICE(price_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_kpival_type
        FOREIGN KEY (kpi_type_id) REFERENCES KPI_TYPE(kpi_type_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 5) DECISION_TYPE
-- ---------------------------------------------------------------------
CREATE TABLE DECISION_TYPE (
    decision_type_id     INT AUTO_INCREMENT PRIMARY KEY,
    decision_name        VARCHAR(30) NOT NULL UNIQUE,
    decision_description TEXT
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 6) DECISION_RULE  (DECISION_TYPE 1:N DECISION_RULE)
-- ---------------------------------------------------------------------
CREATE TABLE DECISION_RULE (
    rule_id          INT AUTO_INCREMENT PRIMARY KEY,
    rule_name        VARCHAR(100) NOT NULL,
    rule_description TEXT,
    decision_type_id INT NOT NULL,
    priority_level   INT DEFAULT 1,
    is_active        BOOLEAN DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rule_dtype
        FOREIGN KEY (decision_type_id) REFERENCES DECISION_TYPE(decision_type_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 7) RULE_CONDITION  (DECISION_RULE N:M KPI_TYPE köprüsü)
-- ---------------------------------------------------------------------
CREATE TABLE RULE_CONDITION (
    condition_id    INT AUTO_INCREMENT PRIMARY KEY,
    rule_id         INT NOT NULL,
    kpi_type_id     INT NOT NULL,
    operator_type   VARCHAR(5) NOT NULL,
    threshold_value DECIMAL(18,6),
    logical_group   VARCHAR(10) DEFAULT 'AND',
    condition_order INT DEFAULT 1,
    CONSTRAINT fk_cond_rule
        FOREIGN KEY (rule_id) REFERENCES DECISION_RULE(rule_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cond_kpi
        FOREIGN KEY (kpi_type_id) REFERENCES KPI_TYPE(kpi_type_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 8) DECISION_RESULT  (STOCK_PRICE 1:1, COMPANY/DECISION_TYPE/RULE 1:N)
-- ---------------------------------------------------------------------
CREATE TABLE DECISION_RESULT (
    decision_result_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    company_id         INT NOT NULL,
    price_id           BIGINT NOT NULL UNIQUE,
    decision_type_id   INT NOT NULL,
    rule_id            INT,
    decision_date      DATE NOT NULL,
    confidence_score   DECIMAL(5,4),
    result_note        TEXT,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_res_company
        FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_res_price
        FOREIGN KEY (price_id) REFERENCES STOCK_PRICE(price_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_res_dtype
        FOREIGN KEY (decision_type_id) REFERENCES DECISION_TYPE(decision_type_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_res_rule
        FOREIGN KEY (rule_id) REFERENCES DECISION_RULE(rule_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 9) ALERT  (DECISION_RESULT 1:N ALERT)
-- ---------------------------------------------------------------------
CREATE TABLE ALERT (
    alert_id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    decision_result_id BIGINT NOT NULL,
    alert_type         VARCHAR(30),
    alert_message      TEXT,
    severity_level     VARCHAR(10),
    alert_date         DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read            BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_alert_result
        FOREIGN KEY (decision_result_id) REFERENCES DECISION_RESULT(decision_result_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =====================================================================
-- ÖRNEK VERİLER
-- =====================================================================
INSERT INTO COMPANY (company_name, ticker_symbol, sector, market) VALUES
('Nike Inc.', 'NKE', 'Consumer Discretionary', 'NYSE');

INSERT INTO KPI_TYPE (kpi_name, description, formula_text, unit) VALUES
('Volatilite',    '30 günlük getiri standart sapması', 'STDDEV(log(close/close_prev)) * sqrt(252)', '%'),
('MA30',          '30 günlük basit hareketli ortalama', 'AVG(close, 30)', 'USD'),
('VolumeAnalysis','Hacim / 30 günlük ortalama hacim',   'volume / AVG(volume,30)', 'ratio');

INSERT INTO DECISION_TYPE (decision_name, decision_description) VALUES
('AL',            'Trend güçlü ve hacim yeterli -> satın al sinyali'),
('BEKLE',         'Koşullar net değil -> pozisyon açma'),
('RISK_UYARISI',  'Yüksek volatilite -> risk uyarısı');
