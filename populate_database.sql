INSERT INTO users (username, password_hash, email, role)
VALUES
	('customer1', '$2b$12$3MKcEpWwiXM7ocpSXQOYeeBqnrOFHYZQti1sebnXP.l9CMLaDmVTS', 'customer1@example.com', 'customer'),
	('customer2', '$2b$12$FbZkr80qHYTzLCjFP3//4.R7.iCQyHRW1zbwde8xd36bN4KqbuLvu', 'customer2@example.com', 'customer'),
	('staff1', '$2b$12$2yha6il4/AHIuw3fe9F6oet8tlcX3kvOEtMHqzqSaGHZplqS6UnRO', 'staff1@example.com', 'staff'),
	('staff2', '$2b$12$lMLo.6Ka5oxiEfKiUzvkR.w2PVBGEXSU2Dx90RfXE7u.EMXd5gmGK', 'staff2@example.com', 'staff'),
	('admin1', '$2b$12$7xzrCLlkpCq4ybjdrVJIM.H56.cnc/BJb87p4aA4usVZBpdMgdm4G', 'admin1@example.com', 'admin');


	-- Insert users with real names and hashed passwords-created by AI.
INSERT INTO users (username, password_hash, email, role) 
VALUES
    ('alice_williams', '$2b$12$ikKJW9sJe7uqaJZ8FOhCv.dutXDHZVUXxvJnYrTviM6ZEXzwiSy4K', 'alice.williams@example.com', 'customer'),
    ('bob_smith', '$2b$12$I4i1Y3DUjZyu98pIewXL0eAdNgJaz77TsjJgFJ.zCpbyLGA83X8z2', 'bob.smith@example.com', 'customer'),
    ('carol_jones', '$2b$12$wR2NW9Q/5nyBKruovv14/eYWWlfPRtAwutSzRtfyOtFk9MVxozNgy', 'carol.jones@example.com', 'customer'),
    ('david_brown', '$2b$12$ISpm51UEc2mRrrKDT7iUueJ9EClI2dw4/401r35h4Vsa/VfZFEdda', 'david.brown@example.com', 'customer'),
    ('emma_davis', '$2b$12$e7uSOR29FP7mdvRSTjg.gekUqO4lVIKZD30swUzWVzHs/Gb49zqBG', 'emma.davis@example.com', 'customer'),
    ('frank_martin', '$2b$12$CdFzhYf1.vTx12RgM3cOseEEaAULfF.OGRxScMF6OHAc0kPTeENmS', 'frank.martin@example.com', 'customer'),
    ('grace_clark', '$2b$12$uid8HO1CyQoncVqUapOB9e2/lOIKfesRin0BRNNhEdtR/tJzOlv9W', 'grace.clark@example.com', 'customer'),
    ('hannah_lee', '$2b$12$5RS4UvBNEzc6CZndWcefkeR3euTmY6KrOKxs7RLeavS9LnW6IPkCq', 'hannah.lee@example.com', 'customer'),
    ('ian_king', '$2b$12$QdXb9ey4Oadqbup1H8onHuyAYhCYVGq1wSZiHVxQw73XYXG7.puD.', 'ian.king@example.com', 'customer'),
    ('jack_moore', '$2b$12$haQu8l/pnQfElXVVIb4nnuBILa0Cg9/VZpaLO76kYcd3KhL2DQvRi', 'jack.moore@example.com', 'customer'),
    ('karen_wilson', '$2b$12$Fqe.aEVFCK1Ypib9kKqADeMUbxl03psfRVXOc7jL1TUl9FIFQJ8DK', 'karen.wilson@example.com', 'customer'),
    ('lucas_taylor', '$2b$12$bi6SmBAMk70RZ.qPiannQO1NnnP.k1j2afOSRntHRCeEhYi5cmU9S', 'lucas.taylor@example.com', 'staff'),
    ('mona_lee', '$2b$12$AeQcAwngIiI22xkKpLTZPeOs6ESjN1URGOy2mCrzootabbYdS/AZK', 'mona.lee@example.com', 'staff'),
    ('noah_sanders', '$2b$12$.upL93KmS8OclWq9ZWYM0eo1UrIQAzJHpf1WvL1zSQJyd1nrdG6Sq', 'noah.sanders@example.com', 'staff'),
    ('olivia_smith', '$2b$12$ER35iZrcW/AYUyIFE81ThOP6wISsR.B2pw2SCmx5QZ1F1TbYm0Qsq', 'olivia.smith@example.com', 'staff'),
    ('paul_baker', '$2b$12$eYDVU8u2/DRm75htoexH1eT.N3cdkVOyIe1oBJUIbrSQay6mSTbPC', 'paul.baker@example.com', 'admin'),
    ('queen_carter', '$2b$12$1VbsW0./0kZF3U3gACf/u.5HxGJ3Ow1rEnT9kuPSkt63OYBpRLpi6', 'queen.carter@example.com', 'admin');

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


UPDATE users
SET
    full_name = CASE 
        WHEN username = 'customer1' THEN 'Customer One'
        WHEN username = 'customer2' THEN 'Customer Two'
        WHEN username = 'staff1' THEN 'Staff One'
        WHEN username = 'staff2' THEN 'Staff Two'
        WHEN username = 'admin1' THEN 'Admin One'
        WHEN username = 'alice_williams' THEN 'Alice Williams'
        WHEN username = 'bob_smith' THEN 'Bob Smith'
        WHEN username = 'carol_jones' THEN 'Carol Jones'
        WHEN username = 'david_brown' THEN 'David Brown'
        WHEN username = 'emma_davis' THEN 'Emma Davis'
        WHEN username = 'frank_martin' THEN 'Frank Martin'
        WHEN username = 'grace_clark' THEN 'Grace Clark'
        WHEN username = 'hannah_lee' THEN 'Hannah Lee'
        WHEN username = 'ian_king' THEN 'Ian King'
        WHEN username = 'jack_moore' THEN 'Jack Moore'
        WHEN username = 'karen_wilson' THEN 'Karen Wilson'
        WHEN username = 'lucas_taylor' THEN 'Lucas Taylor'
        WHEN username = 'mona_lee' THEN 'Mona Lee'
        WHEN username = 'noah_sanders' THEN 'Noah Sanders'
        WHEN username = 'olivia_smith' THEN 'Olivia Smith'
        WHEN username = 'paul_baker' THEN 'Paul Baker'
        WHEN username = 'queen_carter' THEN 'Queen Carter'
        ELSE full_name
    END,
    contact_number = CASE 
        WHEN username = 'customer1' THEN '123-456-7890'
        WHEN username = 'customer2' THEN '234-567-8901'
        WHEN username = 'staff1' THEN '345-678-9012'
        WHEN username = 'staff2' THEN '456-789-0123'
        WHEN username = 'admin1' THEN '567-890-1234'
        WHEN username = 'alice_williams' THEN '123-456-7890'
        WHEN username = 'bob_smith' THEN '234-567-8901'
        WHEN username = 'carol_jones' THEN '345-678-9012'
        WHEN username = 'david_brown' THEN '456-789-0123'
        -- Continue similarly for others
        ELSE contact_number
    END,
    home_address = CASE 
        WHEN username = 'customer1' THEN '123 Green Street, City'
        WHEN username = 'customer2' THEN '234 Blue Avenue, City'
        WHEN username = 'staff1' THEN '345 Red Road, City'
        WHEN username = 'staff2' THEN '456 Yellow Blvd, City'
        WHEN username = 'admin1' THEN '567 White Lane, City'
        WHEN username = 'alice_williams' THEN '123 Green Street, City'
        -- Continue similarly for others
        ELSE home_address
    END,
    profile_image = CASE 
        WHEN username = 'customer1' THEN 'customer1_profile.jpg'
        WHEN username = 'customer2' THEN 'customer2_profile.jpg'
        WHEN username = 'staff1' THEN 'staff1_profile.jpg'
        WHEN username = 'staff2' THEN 'staff2_profile.jpg'
        WHEN username = 'admin1' THEN 'admin1_profile.jpg'
        WHEN username = 'alice_williams' THEN 'alice_profile.jpg'
        -- Continue similarly for others
        ELSE profile_image
    END,
    environmental_interests = CASE 
        WHEN username = 'customer1' THEN 'Recycling, Sustainability'
        WHEN username = 'customer2' THEN 'Energy Conservation, Green Living'
        WHEN username = 'staff1' THEN 'Waste Reduction, Solar Power'
        WHEN username = 'staff2' THEN 'Composting, Urban Farming'
        WHEN username = 'admin1' THEN 'Environmental Policy, Eco Innovation'
        WHEN username = 'alice_williams' THEN 'Green Energy, Water Conservation'
        -- Continue similarly for others
        ELSE environmental_interests
    END;



INSERT INTO users (username, password_hash, email, role)
VALUES
	('zachary_lee', '$2b$12$6Pg55nTWngFkyoxmR.hjBOcWGxYt7QmegsffjZlCzRNx1cC/M/oSq', 'zachary_lee@example.com', 'customer'),
	('april_walker', '$2b$12$Gl4v8WDi1535sJIdhK54peKbULVWXnKUuCPuycGbPascrSC2hQnPm', 'april_walker@example.com', 'customer'),
	('brandon_hall', '$2b$12$IZg/AG5.rVvE4m2aJUqogexmy9kFttI/SFtAzz/cbNBSg8t1Kq4iC', 'brandon_hall@example.com', 'staff'),
	('cynthia_king', '$2b$12$5pQft2ZowstzDk8HgLCw1urIrdaO42WI8YHzimooNUXKPLUgg4NCK', 'cynthia_king@example.com', 'staff'),
	('derek_wright', '$2b$12$wbdF1CjYY9yrCrBTQsI5ceojiZwQJofT4zcw3n5dSVuZR0nVcndby', 'derek_wright@example.com', 'admin'),
	('eric_lopez', '$2b$12$HcZ9xOH0CMx00Y4Dsd9YEe1BhEmrjS9NVOxTmN/AkP94j3qPwcbFu', 'eric_lopez@example.com', 'customer'),
	('fiona_green', '$2b$12$eZOpyVwMtBWKS7e7aeqjCOw3IPjR9NHfJSiWQfEZdqnpjA24QlNEG', 'fiona_green@example.com', 'customer'),
    ('george_adams', '$2b$12$kEoCPim2900d4clj20V5SO5QdomimlWTBUoMFCSogbzsaLDVKSAIq', 'george_adams@example.com', 'customer'),
    ('hannah_baker', '$2b$12$.yUCfttbujSMJZuwhhrsLOweUx2g9DJ1EpiCIYVYX4aE0m4sRAfCS', 'hannah_baker@example.com', 'customer'),
    ('ian_nelson', '$2b$12$.oIhu86Hu1emz1EeXUFnfu58BwvryvJyp.MOHLUPUtU7MDZk8UhBe', 'ian_nelson@example.com', 'customer'),
    ('admin2', '$2b$12$/6RyLblwDYrqt8o12lib/Ou3yxc4bdxoAo4i7aRG0OSNMMAcgKley', 'admin2@example.com', 'admin');



    INSERT INTO events (event_name, event_leader_id, location_, event_type, event_date)
VALUES
    ('Park  pickup', 5, 'Ocean Beach', 'Environmental', '2026-02-01'),
    ('Muriwai Clean-up', 4, 'Long Bay', 'Environmental', '2026-03-15'),
    ('Community Recycling Drive', 3, 'Central Park', 'work', '2026-03-5');


    INSERT INTO eventregistrations (event_id, volunteer_id, attendance, registered_at)
VALUES
    (11, 12, 'Present', '2026-03-0 09:00:00'),
    (12, 13, 'Late', '2026-03-14 09:30:00'),
    (13, 15, 'Present', '2026-03-19 10:00:00'),
    (14, 16, 'Absent', '2026-03-24 11:30:00'),
    (15, 17, 'No-Show', null),
	(16, 12, 'Present', '2026-03-09 10:00:00'),
	(17, 13, 'Present', '2026-03-14 10:30:00'),
	(18, 15, 'Late', '2026-03-19 11:00:00'),
	(19, 16, 'Present', '2026-03-24 12:30:00'),
	(20, 17, 'Excused', null);


'''update users table for where the password_hash was copy pasted with extra spaces, 
we need to trim those spaces to ensure the hashes are correct and can be used for authentication'''
UPDATE users
SET password_hash = trim(password_hash)
WHERE password_hash <> trim(password_hash);