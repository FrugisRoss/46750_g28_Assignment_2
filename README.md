# 46750_g28_Assignment_2

## Overview
This project implements three optimization models for fuel procurement and electricity generation planning. All models minimize fuel purchasing costs while meeting electricity demand constraints over a desired period (2019–2022 in model1, for instance).

## Dataloader
- **Functionality:** this file is not to be opened and run per se, it serves as a function for the model files to retrieve data from the csv files

## Data
- **csv files:** the csv files contain the needed data. If experiments with changed prices, other storage size, plant capacities are of interest these parameters must be changed in the csv files.

## Models

### Model 1: Single month optimization
- **Approach:** Solves a separate optimization problem for the first month specified by startdate disregarding the rest of the data
- **Decision Variables:** Monthly fuel purchases (coal, oil, gas) and generation
- **Use Case:** Baseline comparison; used to demonstrates the benefit of forward-looking planning

### Model 1b: Full time interval
- **Content:** A repeat of Model 1 for every time period in the specified time period. It is the unadultered Model 1 approach in a for loop to have the easiest interpretability for the comparison with Model 2
- **Results:** The cost per month, and the fuel composition bought, and energy generated per fuel type is saved in results/model1/running_cost_results.csv

### Model 2: Full time interval with Storage and Perfect Foresight
- **Approach:** Solves a single optimization problem across all specified months with state-of-charge constraints
- **Decision Variables:** Monthly fuel purchases, consumption, generation, and to some extent storage levels (governed by purchase/consumption)
- **Key Features:**
  - Tracks fuel storage evolution over time
  - Captures efficiency losses in energy conversion
  - Enables fuel arbitrage across time periods
- **Results:** The cost per month, and the fuel composition bought, and energy generated per fuel type is saved in results/model2/model2_results.csv

### Model 3: Full time interval with Scenario Analysis
- **Approach:** Extends Model 2 with 
- **Decision Variables:** Same as Model 2 with 
- **Key Features:**
  - 
- **Results:** saved in a variety of csv files in results/model3 folder

## Data Needed
- **fuel_prices.csv:** Monthly fuel prices (EUR/MWh thermal energy)
- **electricity_demand.csv:** Monthly electricity demand by zone (MWh)
- **plant_capacity.csv:** Plant generation capacity limits (MWh/month)
- **efficiency.csv:** Thermal-to-electric conversion efficiency by fuel type
- **storage.csv:** Maximum fuel storage capacity (tonnes/m³ MWh thermal equivalents)

## Results
- Model 1 results: `results/model1/model1_results.csv`
- Model 2 results: `results/model2/model2_results.csv` 
- Model 3 results: `results/model3/deterministic_results_by_fuel.csv, stochastic_expected_results_by_fuel.csv, scenario_*.csv` 

