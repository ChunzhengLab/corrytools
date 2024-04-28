---
# SPDX-FileCopyrightText: 2017-2023 CERN and the Corryvreckan authors
# SPDX-License-Identifier: CC-BY-4.0 OR MIT
---
# FilterEventsByIntercept
**Maintainer**: Bong-Hwi Lim (<bong-hwi.lim@cern.ch>), Miljenko Suljic (<miljenko.suljic@cern.ch>)
**Module Type**: *GLOBAL*  
**Detector Type**: *all*  
**Status**: Immature

### Description
This module filters the event based on the track intercept position on a plane.

It accepts the event if there is at least one track in the boundary_track_intercept region.

### Parameters
* `boundary_track_intercept`: A region of the local track intercept position to be selected. eg) `[[1,1],[1,2],[2,2],[2,1]]`
* `remove_tracks_out_of_boundary`: If true, remove the tracks that are not in the boundary_track_intercept region. Default is false.

### Plots produced
* 1D histogram of the events filtered by a certain parameter and the total number of filtered events.

### Usage
```toml
[FilterEventsByIntercept]
type = "OPAMP"
boundary_track_intercept=[[1,1],[1,2],[2,2],[2,1]]

```
