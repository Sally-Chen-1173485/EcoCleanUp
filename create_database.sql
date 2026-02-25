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

