/**
 * @file
 * @brief Implementation of module OPAMPDBWriter
 *
 * @copyright Copyright (c) 2020 CERN and the Corryvreckan authors.
 * This software is distributed under the terms of the MIT License, copied verbatim in the file "LICENSE.md".
 * In applying this license, CERN does not waive the privileges and immunities granted to it by virtue of its status as an
 * Intergovernmental Organization or submit itself to any jurisdiction.
 * SPDX-License-Identifier: MIT
 */

#include "OPAMPDBWriter.h"

using namespace corryvreckan;

OPAMPDBWriter::OPAMPDBWriter(Configuration& config, std::vector<std::shared_ptr<Detector>> detectors)
    : Module(config, std::move(detectors)) {}

void OPAMPDBWriter::initialize() {
    // Create output file
    config_.setDefault<std::string>("file_name", "data");
    runNumber = config_.get<std::string>("run_number", "0");
    detectorType = config_.get<std::string>("detector_type", "");
    outputFileName = createOutputFile(config_.get<std::string>("file_name"), "csv", true);
    outputFile = std::make_unique<std::ofstream>(outputFileName);

    // Convert detector type to lowercase
    std::transform(detectorType.begin(), detectorType.end(), detectorType.begin(), ::tolower);

    // Initialise member variables
    m_eventNumber = 0;
    runNumber = runNumber.substr(0, runNumber.find("_"));
    *outputFile << "triggerID,run,eventID,detector,track_intercept_column,track_intercept_row\n";
}

StatusCode OPAMPDBWriter::run(const std::shared_ptr<Clipboard>& clipboard) {
    if(!clipboard->isEventDefined()) {
        ModuleError("No Clipboard event defined, cannot continue");
    }

    auto event = clipboard->getEvent();
    auto tracks = clipboard->getData<Track>();
    for(auto& detector : get_detectors()) {
        std::string dType = detector->getType();
        if(dType.find(detectorType) != std::string::npos) {
            for(auto& track : tracks) {
                auto intercept = detector->getLocalIntercept(track.get());
                *outputFile << (event->triggerList().begin())->first << "," << runNumber << "," << std::setprecision(15)
                            << std::stod(runNumber) * 100000 + (event->triggerList().begin())->first << ","
                            << std::setprecision(6) << detector->getName() << "," << detector->getColumn(intercept) << ","
                            << detector->getRow(intercept) << "\n";
            }
        }
    }

    // Increment event counter
    m_eventNumber++;

    // Return value telling analysis to keep running
    return StatusCode::Success;
}

void OPAMPDBWriter::finalize(const std::shared_ptr<ReadonlyClipboard>&) {
    LOG(DEBUG) << "Analysed " << m_eventNumber << " events";
}
