CREATE DATABASE loginexample;

-- Create enum type first
CREATE TYPE user_role AS ENUM ('customer', 'staff', 'admin');



CREATE TABLE IF NOT EXISTS users (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(20) NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  email VARCHAR(320) NOT NULL,
  person_role user_role NOT NULL
);

DROP TABLE IF EXISTS events;
CREATE TABLE events
(
    event_id SERIAL PRIMARY KEY,
    event_name character varying(100)  NOT NULL,
    event_leader_id integer NOT NULL,
    location_ character varying(255) NOT NULL,
    event_type character varying(50) ,
    event_date date NOT NULL,
    CONSTRAINT fk_user
       FOREIGN KEY (event_leader_id)
       REFERENCES users (user_id)
       ON DELETE CASCADE
       ON UPDATE CASCADE);
   

DROP TABLE IF EXISTS eventoutcomes;
CREATE TABLE IF NOT EXISTS eventoutcomes
(
    outcome_id SERIAL PRIMARY KEY,
    event_id integer NOT NULL,
    num_attendees integer,
    bags_collected integer,
    recyclables_sorted integer,
    other_achievements text ,
    recorded_by integer NOT NULL,
    recorded_at timestamp with time zone,
    CONSTRAINT  fk_event
       FOREIGN KEY (event_id)
       REFERENCES events (event_id)
       ON DELETE CASCADE
       ON UPDATE CASCADE,
    CONSTRAINT fk_user
       FOREIGN KEY (recorded_by)
       REFERENCES users (user_id)
      ON DELETE CASCADE
      ON UPDATE CASCADE);




DROP TABLE IF EXISTS feedback;
CREATE TABLE IF NOT EXISTS feedback
(
    feedback_id SERIAL PRIMARY KEY,
    event_id integer NOT NULL,
    volunteer_id integer NOT NULL,
    rating integer,
    comments text,
    submitted_at timestamp with time zone,
    CONSTRAINT fk_event
       FOREIGN KEY (event_id)
       REFERENCES events (event_id)
       ON DELETE CASCADE
       ON UPDATE CASCADE,
    CONSTRAINT fk_user
       FOREIGN KEY (volunteer_id)
       REFERENCES users (user_id)
       ON DELETE CASCADE
       ON UPDATE CASCADE);



CREATE TYPE attendance_type AS ENUM ('Present', 'Absent', 'Late', 'Excused', 'No-Show', 'Pending');

DROP TABLE IF EXISTS eventregistrations;

CREATE TABLE IF NOT EXISTS eventregistrations
(
    registration_id SERIAL PRIMARY KEY,
    event_id integer NOT NULL,
    volunteer_id integer NOT NULL,
    attendance attendance_type DEFAULT 'Pending',
    registered_at timestamp with time zone,
    CONSTRAINT fk_event
        FOREIGN KEY (event_id)
        REFERENCES events (event_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_user
        FOREIGN KEY (volunteer_id)
        REFERENCES users (user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

--because we are using from a previous template, we need to update the user_role enum and the existing data to match the new roles
ALTER TYPE user_role ADD VALUE 'Volunteers';
ALTER TYPE user_role ADD VALUE 'Event Leaders';
ALTER TYPE user_role ADD VALUE 'Administrators';

UPDATE users SET person_role = 'Volunteers' WHERE person_role = 'customer';
UPDATE users SET person_role = 'Event Leaders' WHERE person_role = 'staff';
UPDATE users SET person_role = 'Administrators' WHERE person_role = 'admin';

--change column to align with the ERD table
ALTER TABLE users RENAME COLUMN person_role TO role;

ALTER TABLE users
  ADD COLUMN full_name VARCHAR(100) NOT NULL DEFAULT '',
  ADD COLUMN contact_number VARCHAR(20),
  ADD COLUMN home_address VARCHAR(255),
  ADD COLUMN profile_image VARCHAR(255),
  ADD COLUMN environmental_interests VARCHAR(255);
  ALTER COLUMN username TYPE VARCHAR(50);

ALTER TABLE users
ALTER COLUMN username TYPE VARCHAR(50);

ALTER TABLE users
ALTER COLUMN email TYPE VARCHAR(100);

CREATE TYPE status_setting AS ENUM ('active', 'nonactive', 'banned', 'suspended');
ALTER TABLE users
  ADD COLUMN status status_setting NOT NULL DEFAULT 'active';

ALTER TABLE events
  ADD COLUMN start_time TIME,
  ADD COLUMN end_time TIME,
  ADD COLUMN duration integer,
  ADD COLUMN description_ text,
  ADD COLUMN supplies TEXT,
  ADD COLUMN safety_instructions TEXT, 
  ADD COLUMN created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP;