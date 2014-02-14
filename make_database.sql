BEGIN TRANSACTION;

DROP TABLE if EXISTS example;

CREATE TABLE example ( token     TEXT,
       	     	     events    TEXT,
       	     	     rui       TEXT,
		     expertise INTEGER,
		     grp       INTEGER,
		     offset    REAL
		     );

--Expertise:
-- 0: No assessment
-- 1: Novice
-- 2: Intermediate
-- 3: Expert

--
-- example01
--
INSERT INTO example VALUES (
       	    	  	 "example01",
			 "example01_events.txt",
       	    	  	 "example01_rui.txt",
			 1,
			 1,
			 0
			 );


COMMIT;