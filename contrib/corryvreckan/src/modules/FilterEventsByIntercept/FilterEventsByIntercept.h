/**
 * @file
 * @brief Definition of module FilterEventsByIntercept
 *
 * @copyright Copyright (c) 2020 CERN and the Corryvreckan authors.
 * This software is distributed under the terms of the MIT License, copied verbatim in the file "LICENSE.md".
 * In applying this license, CERN does not waive the privileges and immunities granted to it by virtue of its status as an
 * Intergovernmental Organization or submit itself to any jurisdiction.
 * SPDX-License-Identifier: MIT
 */

#include <TCanvas.h>
#include <TH1F.h>
#include <TH2F.h>
#include <iostream>
#include "core/module/Module.hpp"
#include "objects/Cluster.hpp"
#include "objects/Pixel.hpp"
#include "objects/Track.hpp"

namespace corryvreckan {
    /** @ingroup Modules
     * @brief Module to do function
     *
     * More detailed explanation of module
     */
    class FilterEventsByIntercept : public Module {

    public:
        /**
         * @brief Constructor for this unique module
         * @param config Configuration object for this module as retrieved from the steering file
         * @param detector Pointer to the detector for this module instance
         */
        FilterEventsByIntercept(Configuration& config, std::shared_ptr<Detector> detector);

        /**
         * @brief [Initialise this module]
         */
        void initialize() override;

        /**
         * @brief [Run the function of this module]
         */
        StatusCode run(const std::shared_ptr<Clipboard>& clipboard) override;

        /**
         * @brief [Finalise module]
         */
        void finalize(const std::shared_ptr<ReadonlyClipboard>& clipboard) override;

    private:
        bool FilterTrackPos(const std::shared_ptr<Detector> detector, const std::shared_ptr<Clipboard>& clipboard);

        // Referenced from PixelDetector class, just updated to use float instead of int
        int winding_number(std::pair<float, float> probe, std::vector<std::vector<float>> polygon);
        float isLeft(std::pair<float, float> pt0, std::pair<float, float> pt1, std::pair<float, float> pt2);

        TH1F* hFilter_;

        std::vector<std::vector<float>> boundaryTrackIntercept;
        bool removeTracksOutOfBoundary;
    };

} // namespace corryvreckan
