
CREATE TABLE banned_domain (
    id int  NOT NULL,
    domain text  NOT NULL,
    CONSTRAINT banned_domain_pk PRIMARY KEY (id)
);

CREATE TABLE domain_ip_cache (
    id int  NOT NULL,
    banned_domain_id int  NOT NULL,
    ip text  NOT NULL,
    CONSTRAINT domain_ip_cache_pk PRIMARY KEY (id)
);


ALTER TABLE domain_ip_cache ADD CONSTRAINT Table_9_domain_blacklist
    FOREIGN KEY (banned_domain_id)
    REFERENCES banned_domain (id)  
    NOT DEFERRABLE 
    INITIALLY IMMEDIATE
;

CREATE SEQUENCE banned_domain_seq
     INCREMENT BY 1
     NO MINVALUE
     NO MAXVALUE
     START WITH 1000
     NO CYCLE
;
