CREATE TABLE HEIMDALL_cand(
   ID INTEGER,
   DetectionSNR FLOAT(7,4),
   CandidateSampleNumber INT,
   CandidateTime DOUBLE(8,4),
   BoxcarFilterNumber INT,
   DispersionMeasureTrialNumber INT,
   DispersionMeasure FLOAT(7,4),
   MembersInCluster INT,
   FirstCandidateSample INT,
   LastCandidateSample INT,
   PRIMARY KEY (ID)
);
