Strategies for Reuse of Launch Vehicle First Stages
===================================================

This repository provides supporting materials for the paper "Strategies for Reuse of Launch Vehicle First Stages" presented by Matthew Vernacchia and Kelly Mathesius at the 2018 Interantion Astronautical Congress (paper code IAC-18,D2,4,3, x47508).


# Abstract

Many strategies have been proposed for recovery and reuse of launch vehicle first stages in an effort to reduce cost per flight and expand access to space. Although a reusable first stage has been operated (Falcon 9) and several others are under development, there is still much debate as to which first stage reuse strategy, if any, is economically worthwhile. To address this, an analysis was performed of the payload performance and cost of all major first stage recovery strategies, under common assumptions. The analyzed strategies include propulsive landing (downrange or at the launch site), winged stages (air-breathing fly-back to the launch site or downrange glider recovery), and recovery via parachutes.

This paper establishes a general model to compare the payload capacity and cost per flight of first stage reuse strategies. The payload capacity model is neatly derived from physical first principles and cost estimation uses the TRANSCOST model. Model uncertainty is examined using Monte Carlo techniques, and the sensitivity of cost to various technological and operational factors is assessed.

This study finds that downrange, propulsive-landing recovery of the full first stage is the most cost-effective strategy, and could have a cost per flight 1/3 to 2/3 that of an expandable launch vehicle with equivalent payload capacity. First stage reuse is only worthwhile for larger launch vehicles - the cost of small launch vehicles is dominated by operations and support, not hardware. Finally, the cost savings from reuse can only pay off the development effort if launch rates are high (more than about 20/year). New LEO constellations could provide the high-volume, cost-sensitive launch demand under which reuse is economically worthwhile.


# Using this repository

The paper can be found in the `paper` directory, and the presentation given at IAC 2018 in the `presentations/IAC2018` directory. The software used to perform the cost and performance modeling is provided as a python package in the `lvreuse` directory. The framework of the cost model is implemented in `lvreuse/cost`, and the performance model in `lvreuse/performance`.  The Monte Carlo analysis and other investigations of the model results are implemented in `lvreuse/analysis`.

The software, paper and presentation materials may be freely shared under the MIT License, although the authors retain the copyright.

If you have questions about this work, want help using the software, or are interested in collaboration please contact Matthew Vernacchia at mvernacc@mit.edu.


# Installation

This software relies on python 3 and the scipy stack.

The Monte Carlo analysis uses the Rhodium library by David Hadka. You will need to download and install our fork of Rhodium from https://github.com/mvernacc/Rhodium. 
