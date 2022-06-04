CREATE TABLE accounts (	
	user_id serial PRIMARY KEY,
	username VARCHAR ( 50 ) UNIQUE NOT NULL,
	password text NOT NULL,
	email VARCHAR ( 255 ) UNIQUE NOT NULL,
	role VARCHAR (255) NOT NULL, 
	created_on TIMESTAMP NOT NULL,
    last_login TIMESTAMP 
);

CREATE TABLE discussion_areas (
    area_id serial PRIMARY KEY,
    full_name VARCHAR ( 100 ) UNIQUE NOT NULL,
    created_at TIMESTAMP,
    last_updated TIMESTAMP,
    creator VARCHAR,
    secretarea boolean
);

CREATE TABLE chains (
    chain_id serial PRIMARY KEY,
    area_id int NOT NULL,
    full_name VARCHAR ( 100 ) UNIQUE NOT NULL,description VARCHAR ( 250 ),
    created_at TIMESTAMP,
    last_updated TIMESTAMP,
    creator VARCHAR
);

CREATE TABLE message (
    message_id serial PRIMARY KEY,
	area_id int NOT NULL,
	chain_id int NOT NULL,
	full_name VARCHAR ( 100 ),
	message_text varchar,
	created_at timestamp,
	creator VARCHAR
);

CREATE TABLE arearights (
    id serial PRIMARY KEY,
    area_id int NOT NULL,
    user_id int  NOT NULL
);

