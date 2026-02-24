CREATE DATABASE loginexample;

-- Create enum type first
CREATE TYPE user_role AS ENUM ('customer', 'staff', 'admin');

CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(20) NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  email VARCHAR(320) NOT NULL,
  person_role user_role NOT NULL
);
