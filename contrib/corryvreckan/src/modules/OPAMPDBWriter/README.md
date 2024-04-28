---
# SPDX-FileCopyrightText: 2017-2023 CERN and the Corryvreckan authors
# SPDX-License-Identifier: CC-BY-4.0 OR MIT
---
# OPAMPDBWriter
**Maintainer**: Bong-Hwi Lim (bong-hwi.lim@cern.ch)
**Module Type**: *GLOBAL*  
**Status**: Immature

### Description
This module writes the data used in OPAMP timing analysis to a file.

### Parameters
* `file_name` : Name of the data file to create, relative to the output directory of the framework. The file extension `.csv` will be appended if not present.
* `run_number` : Run number to be written to the database. Doesn't do anything; it is taken as is from the config file and written to the file. 
* `detectorType` : Detector type to be written to the database.

### Plots produced
None.

### Usage
```toml
[OPAMPDBWriter]
file_name = "OPAMP_DB"
run_number = "@RunNumber@"
detectorType = "OPAMP"
```
