CREATE TABLE IF NOT EXISTS `alert_dev`.`Scenario_AMBER` (
  `ID` INT(11) NOT NULL,
  `OPENCL_PLATFORM` INT(11) NULL DEFAULT '0',
  `OPENCL_DEVICE` INT(11) NULL DEFAULT '0',
  `DEVICE_NAME` VARCHAR(50) NULL DEFAULT 'arts1_25000',
  `DEVICE_PADDING` INT(11) NULL DEFAULT '128',
  `DEVICE_THREADS` INT(11) NULL DEFAULT '32',
  `ITERATIONS` INT(11) NULL DEFAULT '7',
  `MIN_THREADS` INT(11) NULL DEFAULT '8',
  `MAX_THREADS` INT(11) NULL DEFAULT '1024',
  `MAX_ITEMS` INT(11) NULL DEFAULT '63',
  `MAX_UNROLL` INT(11) NULL DEFAULT '1',
  `MAX_DIM0` INT(11) NULL DEFAULT '1024',
  `MAX_DIM1` INT(11) NULL DEFAULT '128',
  `MAX_ITEMS_DIM0` INT(11) NULL DEFAULT '64',
  `MAX_ITEMS_DIM1` INT(11) NULL DEFAULT '32',
  `SUBBANDING` TINYINT(1) NULL DEFAULT '1',
  `SNR` VARCHAR(25) NULL DEFAULT 'MOMSIGMACUT',
  `CHANNELS` INT(11) NULL DEFAULT '1536',
  `MIN_FREQ` DOUBLE(8,4) NULL DEFAULT '1250.0977',
  `CHANNEL_BANDWIDTH` INT(11) NULL DEFAULT '0',
  `SAMPLES` INT(11) NULL DEFAULT '12500',
  `SAMPLING_TIME` DOUBLE(8,4) NULL DEFAULT '0.0001',
  `DOWNSAMPLING` INT(11) NULL DEFAULT '1',
  `SUBBANDS` INT(11) NULL DEFAULT '32',
  `SUBBANDING_DMS` INT(11) NULL DEFAULT '128',
  `SUBBANDING_DM_FIRST` DOUBLE(8,4) NULL DEFAULT '5.0000',
  `SUBBANDING_DM_STEP` DOUBLE(8,4) NULL DEFAULT '6.4000',
  `DMS` INT(11) NULL DEFAULT '32',
  `DM_FIRST` DOUBLE(8,4) NULL DEFAULT '0.0000',
  `DM_STEP` DOUBLE(8,4) NULL DEFAULT '0.2000',
  `BEAMS` INT(11) NULL DEFAULT '1',
  `SYNTHESIZED_BEAMS` INT(11) NULL DEFAULT '1',
  `INTEGRATION_STEPS` INT(11) NULL DEFAULT '5',
  `ZAPPED_CHANNELS` INT(11) NULL DEFAULT NULL,
  `MEDIAN_STEP` INT(11) NULL DEFAULT '5',
  `NSIGMA` INT(11) NULL DEFAULT '3',
  PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS `alert_dev`.`Configuration_AMBER` (
  `ID` INT(11) NOT NULL,
  `CONFIGURATION_NAME` VARCHAR(300) NULL DEFAULT NULL,
  `CONFIGURATION_PATH` VARCHAR(500) NULL DEFAULT NULL,
  `Scenario_ID` INT NOT NULL,
  PRIMARY KEY (`ID`, `Scenario_ID`),
  CONSTRAINT `ID`
    FOREIGN KEY (`Scenario_ID`)
    REFERENCES `alert_dev`.`Scenario_AMBER` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);
CREATE TABLE IF NOT EXISTS `alert_dev`.`HEIMDALL_cand` (
  `ID` INT(11) NOT NULL,
  `DetectionSNR` FLOAT(7,4) NULL DEFAULT NULL,
  `CandidateSampleNumber` INT(11) NULL DEFAULT NULL,
  `CandidateTime` DOUBLE(8,4) NULL DEFAULT NULL,
  `BoxcarFilterNumber` INT(11) NULL DEFAULT NULL,
  `DispersionMeasureTrialNumber` INT(11) NULL DEFAULT NULL,
  `DispersionMeasure` FLOAT(7,4) NULL DEFAULT NULL,
  `MembersInCluster` INT(11) NULL DEFAULT NULL,
  `FirstCandidateSample` INT(11) NULL DEFAULT NULL,
  `LastCandidateSample` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS `alert_dev`.`AMBER_Trigger` (
  `ID` INT(11) NOT NULL,
  `beam_id` INT(11) NULL DEFAULT NULL,
  `batch_id` INT(11) NULL DEFAULT NULL,
  `sample_id` INT(11) NULL DEFAULT NULL,
  `integration_step` INT(11) NULL DEFAULT NULL,
  `compacted_integration_steps` INT(11) NULL DEFAULT NULL,
  `time_stamp` FLOAT(7,4) NULL DEFAULT NULL,
  `DM_id` INT(11) NULL DEFAULT NULL,
  `DM` FLOAT(7,4) NULL DEFAULT NULL,
  `compacted_DMs` INT(11) NULL DEFAULT NULL,
  `SNR` FLOAT(7,4) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS `alert_dev`.`Input_file` (
  `ID` INT(11) NOT NULL,
  `Filename` VARCHAR(100) NULL DEFAULT NULL,
  `Location` VARCHAR(2000) NULL DEFAULT NULL,
  `Description` VARCHAR(200) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`)
);
CREATE TABLE IF NOT EXISTS `alert_dev`.`Input_Results` (
  `Input_ID` INT(11) NOT NULL,
  `Heimdall_ID` INT NULL,
  `Amber_ID` INT NULL,
  `Configuration_ID` INT(11) NULL,
  PRIMARY KEY (`Input_ID`),
  INDEX `ID_idx` (`Heimdall_ID` ASC),
  INDEX `ID_idx1` (`Amber_ID` ASC),
  CONSTRAINT `Input_ID`
    FOREIGN KEY (`Input_ID`)
    REFERENCES `alert_dev`.`Input_file` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `Heimdall_ID`
    FOREIGN KEY (`Heimdall_ID`)
    REFERENCES `alert_dev`.`HEIMDALL_cand` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `Amber_ID`
    FOREIGN KEY (`Amber_ID`)
    REFERENCES `alert_dev`.`AMBER_Trigger` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `Configuration_ID`
    FOREIGN KEY (`Configuration_ID`)
    REFERENCES `alert_dev`.`Configuration_AMBER` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);
