/**
 * @file
 * @brief Implementation of module FilterEventsByIntercept
 *
 * @copyright Copyright (c) 2020 CERN and the Corryvreckan authors.
 * This software is distributed under the terms of the MIT License, copied verbatim in the file "LICENSE.md".
 * In applying this license, CERN does not waive the privileges and immunities granted to it by virtue of its status as an
 * Intergovernmental Organization or submit itself to any jurisdiction.
 * SPDX-License-Identifier: MIT
 */

#include "FilterEventsByIntercept.h"

using namespace corryvreckan;

FilterEventsByIntercept::FilterEventsByIntercept(Configuration& config, std::shared_ptr<Detector> detector)
    : Module(config, std::move(detector)) {}

void FilterEventsByIntercept::initialize() {
    boundaryTrackIntercept = config_.getMatrix<float>("boundary_track_intercept", std::vector<std::vector<float>>());
    removeTracksOutOfBoundary = config_.get<bool>("remove_tracks_out_of_boundary", false);

    if(boundaryTrackIntercept.size() < 3) {
        throw InvalidValueError(config_, "boundary_track_intercept", "Not enough values given (at least 3 required)");
    }

    // QA plots
    hFilter_ = new TH1F("FilteredEvents", "Events filtered;events", 4, 0.5, 4.5);
    hFilter_->GetXaxis()->SetBinLabel(1, "Events");
    hFilter_->GetXaxis()->SetBinLabel(2, "Track intercept position passed");
    hFilter_->GetXaxis()->SetBinLabel(3, "Track intercept position rejected");
    hFilter_->GetXaxis()->SetBinLabel(4, "Events passed ");
}

StatusCode FilterEventsByIntercept::run(const std::shared_ptr<Clipboard>& clipboard) {
    hFilter_->Fill(1);
    auto returnStatus = StatusCode::Success;
    for(auto& detector : get_detectors()) {
        returnStatus = (FilterTrackPos(detector, clipboard)) ? StatusCode::Success : StatusCode::DeadTime;
        if(returnStatus == StatusCode::DeadTime)
            break;
    }
    if(returnStatus == StatusCode::Success)
        hFilter_->Fill(4);
    return returnStatus;
}
bool FilterEventsByIntercept::FilterTrackPos(const std::shared_ptr<Detector> detector,
                                             const std::shared_ptr<Clipboard>& clipboard) {
    bool returnStatus = false;

    auto tracks = clipboard->getData<Track>();
    for(auto& track : tracks) {
        auto intercept = detector->getLocalIntercept(track.get());
        auto coordinates = std::make_pair(static_cast<float>(detector->getColumn(intercept)),
                                          static_cast<float>(detector->getRow(intercept)));
        if(winding_number(coordinates, boundaryTrackIntercept) != 0) {
            returnStatus = true;
            if(!removeTracksOutOfBoundary)
                break;
        } else if(removeTracksOutOfBoundary) {
            clipboard->removeData(track);
        } else {
            returnStatus = false;
        }
    }
    (returnStatus) ? hFilter_->Fill(2) : hFilter_->Fill(3);
    return returnStatus;
}

/* Winding number test for a point in a polygon
 * via: http://geomalgorithms.com/a03-_inclusion.html
 *      Input:   x, y = a point,
 *               polygon = vector of vertex points of a polygon V[n+1] with V[n]=V[0]
 *      Return:  wn = the winding number (=0 only when P is outside)
 */
int FilterEventsByIntercept::winding_number(std::pair<float, float> probe, std::vector<std::vector<float>> polygon) {
    // Two points don't make an area
    if(polygon.size() < 3) {
        LOG(DEBUG) << "No Boundary given.";
        return 0;
    }

    int wn = 0; // the  winding number counter

    // loop through all edges of the polygon

    // edge from V[i] to  V[i+1]
    for(size_t i = 0; i < polygon.size(); i++) {
        auto point_this = std::make_pair(polygon.at(i).at(0), polygon.at(i).at(1));
        auto point_next = (i + 1 < polygon.size() ? std::make_pair(polygon.at(i + 1).at(0), polygon.at(i + 1).at(1))
                                                  : std::make_pair(polygon.at(0).at(0), polygon.at(0).at(1)));

        // start y <= P.y
        if(point_this.second <= probe.second) {
            // an upward crossing
            if(point_next.second > probe.second) {
                // P left of  edge
                if(isLeft(point_this, point_next, probe) > 0) {
                    // have  a valid up intersect
                    ++wn;
                }
            }
        } else {
            // start y > P.y (no test needed)

            // a downward crossing
            if(point_next.second <= probe.second) {
                // P right of  edge
                if(isLeft(point_this, point_next, probe) < 0) {
                    // have  a valid down intersect
                    --wn;
                }
            }
        }
    }
    return wn;
}
/* isLeft(): tests if a point is Left|On|Right of an infinite line.
 * via: http://geomalgorithms.com/a03-_inclusion.html
 *    Input:  three points P0, P1, and P2
 *    Return: >0 for P2 left of the line through P0 and P1
 *            =0 for P2  on the line
 *            <0 for P2  right of the line
 *    See: Algorithm 1 "Area of Triangles and Polygons"
 */
float FilterEventsByIntercept::isLeft(std::pair<float, float> pt0,
                                      std::pair<float, float> pt1,
                                      std::pair<float, float> pt2) {
    return ((pt1.first - pt0.first) * (pt2.second - pt0.second) - (pt2.first - pt0.first) * (pt1.second - pt0.second));
}
void FilterEventsByIntercept::finalize(const std::shared_ptr<ReadonlyClipboard>&) {
    LOG(STATUS) << "Skipped " << hFilter_->GetBinContent(3) << " events. Events passed " << hFilter_->GetBinContent(2);
}
