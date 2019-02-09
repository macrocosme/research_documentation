CREATE TABLE AMBERT_Trigger(
   ID INTEGER,
   beam_id INT,
   batch_id INT,
   sample_id INT,
   integration_step INT,
   compacted_integration_steps INT,
   time_stamp FLOAT(7,4),
   DM_id INT,
   DM FLOAT(7,4),
   compacted_DMs INT,
   SNR FLOAT(7,4),
   PRIMARY KEY (ID)
);
