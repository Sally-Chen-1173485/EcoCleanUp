INSERT INTO users (username, password_hash, email, role)
VALUES
	('customer1', '$2b$12$3W3b9AnL6umkIBm6THGHB.yId0/GuR/Gi7R8ZevTwR0xi3o8rrvZa', 'customer1@example.com', 'customer'),
	('customer2', '$2b$12$6KPIL1c77kZpDXzDDRuJV.ielxGNDUIJPkxl0K5JdQoZTMrcIMBym', 'customer2@example.com', 'customer'),
	('staff1', '$2b$12$OKt92QtCTJmhr4wqRMYZH.6lOSBUh0oGKcvaNerR2fQe6L7.ViQ0O', 'staff1@example.com', 'staff'),
	('staff2', '$2b$12$mT8QI2wKBvpoOFZsRwaLkeuS9FS4vc6sX.GJNnNMA1EKmypk6UYGa', 'staff2@example.com', 'staff'),
	('admin1', '$2b$12$.jUTmK8lb/4O8O3oFuHyeerUl9qs1c.slhGzpYDMJqxGnnToGPuMO', 'admin1@example.com', 'admin');


	-- Insert users with real names and hashed passwords-created by AI.
INSERT INTO users (username, password_hash, email, role) 
VALUES
    ('alice_williams', '$2b$12$3W3b9AnL6umkIBm6THGHB.yId0/GuR/Gi7R8ZevTwR0xi3o8rrvZa', 'alice.williams@example.com', 'customer'),
    ('bob_smith', '$2b$12$6KPIL1c77kZpDXzDDRuJV.ielxGNDUIJPkxl0K5JdQoZTMrcIMBym', 'bob.smith@example.com', 'customer'),
    ('carol_jones', '$2b$12$OKt92QtCTJmhr4wqRMYZH.6lOSBUh0oGKcvaNerR2fQe6L7.ViQ0O', 'carol.jones@example.com', 'customer'),
    ('david_brown', '$2b$12$mT8QI2wKBvpoOFZsRwaLkeuS9FS4vc6sX.GJNnNMA1EKmypk6UYGa', 'david.brown@example.com', 'customer'),
    ('emma_davis', '$2b$12$.jUTmK8lb/4O8O3oFuHyeerUl9qs1c.slhGzpYDMJqxGnnToGPuMO', 'emma.davis@example.com', 'customer'),
    ('frank_martin', '$2b$12$4gXtIsvO4vBzCBaIH5dqkqOXPSR0LnTEXJxjRz3yKHZYPX7eFOm8s', 'frank.martin@example.com', 'customer'),
    ('grace_clark', '$2b$12$L8cR6ZmcOwzIhDhVmSeRbUGAOTzSbF1VRhUp68zN8pTOHgVlw0CBG', 'grace.clark@example.com', 'customer'),
    ('hannah_lee', '$2b$12$X7dd57dgght5t69gggm0yObvn6T7.BH7Iuvbpt7ANv7fRePhE3uSK', 'hannah.lee@example.com', 'customer'),
    ('ian_king', '$2b$12$TyKmJj0sdvlYNOjVhXJgCXYq3VZPBoByB1UQHg31m0uGhT2I0qq3q', 'ian.king@example.com', 'customer'),
    ('jack_moore', '$2b$12$Yj5VQna.5l0DtYPR7MjgW8X5hDpNK6tpoQ9Te0R0GubnNpmCZhbyC', 'jack.moore@example.com', 'customer'),
    ('karen_wilson', '$2b$12$MB7TfFzKftXtdJUqT0MzD9R8xHa9vRzRzmU8u7Z1OZt1l6ERu2bQy', 'karen.wilson@example.com', 'customer'),
    ('lucas_taylor', '$2b$12$DJ9.QcsVhptAd5tw78dlFq6ro/NY3OQwGtwTyF0QTGNNmL47bsccK', 'lucas.taylor@example.com', 'staff'),
    ('mona_lee', '$2b$12$AZPlnXt3VwA0FCmyi7g2p7SvkOgxuwb91StJlxOsmHXt72FESX4qa', 'mona.lee@example.com', 'staff'),
    ('noah_sanders', '$2b$12$PQCp5tqX0RpmwPC1HqbgMw49LlwHrxVsHKc02BZZlXiQy5sl8fi5g', 'noah.sanders@example.com', 'staff'),
    ('olivia_smith', '$2b$12$cb6.lW0gG5z.m9gFfb.mwVAsD1V7jYZ9DQ8m7jAHHKnA1ZRTZ2R9S', 'olivia.smith@example.com', 'staff'),
    ('paul_baker', '$2b$12$y2iTmk6PZmG2aH8Xkgf1tT8J2H1sAk7Zj0pewfeJbwE94Uk6P7eHC', 'paul.baker@example.com', 'admin'),
    ('queen_carter', '$2b$12$7DGRRDCrcmWVzIHoLgB3Oeu1mrRtdJguyg6djm8tZgS8Vsf4ZZ5Wa', 'queen.carter@example.com', 'admin');

-- Insert events (20 events)
INSERT INTO events (event_name, event_leader_id, location_, event_type, event_date)
VALUES
    ('Beach Cleanup', 2, 'Ocean Beach', 'Environmental', '2026-03-10'),
    ('Park Clean-up', 5, 'Central Park', 'Environmental', '2026-03-15'),
    ('River Clean-up', 1, 'Hudson River', 'Environmental', '2026-03-20'),
    ('Forest Restoration', 3, 'Blue Mountains', 'Environmental', '2026-03-25'),
    ('Community Cleanup', 4, 'Main Street', 'Environmental', '2026-04-01'),
    ('Waste Management Workshop', 5, 'City Hall', 'Workshop', '2026-04-05'),
    ('Recycling Awareness Event', 3, 'Green Park', 'Awareness', '2026-04-10'),
    ('Beach Cleanup', 2, 'Coastal Area', 'Environmental', '2026-04-15'),
    ('Park Replanting', 5, 'Springfield Park', 'Environmental', '2026-04-20'),
    ('Urban Garden Initiative', 3, 'Downtown', 'Workshop', '2026-04-25'),
    ('Clean Water Project', 4, 'Shoreline', 'Environmental', '2026-05-01'),
    ('Recycling Fair', 1, 'Market Square', 'Fair', '2026-05-05'),
    ('Wildlife Habitat Preservation', 2, 'River Valley', 'Environmental', '2026-05-10'),
    ('Eco-Friendly Festival', 5, 'City Center', 'Festival', '2026-05-15'),
    ('Sustainable Gardening Workshop', 1, 'Greenhouse', 'Workshop', '2026-05-20'),
    ('Plastic-Free Campaign', 4, 'Community Center', 'Awareness', '2026-05-25'),
    ('Forest Fire Recovery', 3, 'Mountain Area', 'Environmental', '2026-06-01'),
    ('Eco-Conscious Living Workshop', 5, 'University Hall', 'Workshop', '2026-06-05'),
    ('Solar Panel Installation', 4, 'Urban Area', 'Workshop', '2026-06-10'),
    ('Waste-to-Energy Initiative', 2, 'City Waste Facility', 'Environmental', '2026-06-15');

-- Insert event outcomes (sample data for a few events)
INSERT INTO eventoutcomes (event_id, num_attendees, bags_collected, recyclables_sorted, other_achievements, recorded_by, recorded_at)
VALUES
    (1, 20, 150, 120, 'Great teamwork', 5, '2026-03-10 18:30:00'),
    (2, 15, 100, 80,'Volunteers collected extra trash', 3, '2026-03-15 16:00:00'),
    (3, 25, 200, 150,'Removed plastic waste', 4, '2026-03-20 17:00:00'),
    (4, 10, 50, 45,'Planted native species', 2, '2026-03-25 14:30:00'),
    (5, 180, 140, 0,'Engaged local community', 1, '2026-04-01 12:00:00');

-- Insert feedback (sample for different events)
INSERT INTO feedback (event_id, volunteer_id, rating, comments, submitted_at)
VALUES
    (1, 1, 5, 'Great event, would love to join again!', '2026-03-11 08:00:00'),
    (2, 2, 4, 'Good event, but could be better organized.', '2026-03-16 09:00:00'),
    (3, 3, 5, 'Loved the teamwork!', '2026-03-21 09:30:00'),
    (4, 4, 3, 'It was okay, but the weather was bad.', '2026-03-26 10:00:00'),
	(5, 5, 5, 'Great community involvement!', '2026-04-02 11:00:00');

INSERT INTO eventregistrations (event_id, volunteer_id, attendance, registered_at)
VALUES
    (1, 1, 'Present', '2026-03-09 09:00:00'),
    (2, 2, 'Late', '2026-03-14 09:30:00'),
    (3, 3, 'Present', '2026-03-19 10:00:00'),
    (4, 4, 'Absent', '2026-03-24 11:30:00'),
    (5, 5, 'No-Show', null),
	(6, 1, 'Present', '2026-03-09 10:00:00'),
	(7, 2, 'Present', '2026-03-14 10:30:00'),
	(8, 3, 'Late', '2026-03-19 11:00:00'),
	(9, 4, 'Present', '2026-03-24 12:30:00'),
	(10, 5, 'Excused', null);