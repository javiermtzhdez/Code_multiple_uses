#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 11:25:25 2024

@author: cyberdim
"""

import pandas as pd

import xml.etree.ElementTree as ET

import re

# XML reading

# Only designed for AEA website.

# https://www.aeaweb.org/joe/listings?q=eNplj1Fqw0AMRO-i7wSMaX58gEChdxDKrupsq2iNtHYxIXePDDEE-lwn3oykmTt8FW9FRz9Xu8Fwh6JIqZWFYYAODvDL61-1jM5k6RowmHM4qsKgs8gBflj2sbjP22bf9R_Hrg9vtTIWJfn8p6Q6a7MVjce3Y04LZ_yuktl8h4k0l0yN0ZPR7VwivCvGibVhVVl3JK9GGLHZ8BJCtArW5i01UvyWaQp62gpONL6uPR5PmeRcXNU,


#Steps
# 1 Go to aea,
# 2 Download the xml file
# 3 Run this script. 


""" 
The type of jobs are:
US: Full-Time Academic (Permanent, Tenure Track or Tenured)

US: Other Academic (Visiting or Temporary)

US: Other Academic (Part-time or Adjunct)

International:Full-Time Academic (Permanent, Tenure Track or Tenured)

International: Other Academic (Visiting or Temporary)

International: Other Academic (Part-time or Adjunct)

Full-Time Nonacademic

Other Nonacademic (Temporary, Part-Time, Non-Salaried, Consulting, Etc.)
"""

"""
JEL Categories
"""

categories_dict = {
    'A': 'General Economics and Teaching',
    'B': 'History of Economic Thought, Methodology, and Heterodox Approaches',
    'C': 'Mathematical and Quantitative Methods',
    'D': 'Microeconomics',
    'E': 'Macroeconomics and Monetary Economics',
    'F': 'International Economics',
    'G': 'Financial Economics',
    'H': 'Public Economics',
    'I': 'Health, Education, and Welfare',
    'J': 'Labor and Demographic Economics',
    'K': 'Law and Economics',
    'L': 'Industrial Organization',
    'M': 'Business Administration and Business Economics • Marketing • Accounting • Personnel Economics',
    'N': 'Economic History',
    'O': 'Economic Development, Innovation, Technological Change, and Growth',
    'P': 'Political Economy and Comparative Economic Systems',
    'Q': 'Agricultural and Natural Resource Economics • Environmental and Ecological Economics',
    'R': 'Urban, Rural, Regional, Real Estate, and Transportation Economics',
    'Y': 'Miscellaneous Categories',
    'Z': 'Other Special Topics'
}

categories = pd.DataFrame(list(categories_dict.items()), columns=['Code', 'Description'])


# initial path to xml: 
xml_path1 = '/Users/cyberdim/Downloads/joe_full_xml (1).xml' # Change your path here!
xml_path_update = '/Users/cyberdim/Downloads/joe_full_xml.xml' # Change your path here!


############################ FIRST TIME PARSING THIS FILE ############################ 
############################ FIRST TIME PARSING THIS FILE ############################ 
############################ FIRST TIME PARSING THIS FILE ############################ 





# Function to parse the XML and extract position data

def extract_position_data(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # List to hold the data
    data = []

    # Loop through each 'position' tag
    for position in root.findall(".//position"):
        # Dictionary to hold the data for each position
        position_data = {
            'jp_id': position.attrib.get('jp_id', ''),
            'jp_section': position.findtext('jp_section', ''),
            'jp_title': position.findtext('jp_title', ''),
            'jp_institution': position.findtext('jp_institution', ''),
            'jp_division': position.findtext('jp_division', ''),
            'jp_department': position.findtext('jp_department', ''),
            'jp_salary_range': position.findtext('jp_salary_range', ''),
            'jp_full_text': position.findtext('jp_full_text', ''),
            'jp_keywords': position.findtext('jp_keywords', '')
        }

        # Extract and format the application deadline (keep only year, month, day)
        application_deadline = position.findtext('jp_application_deadline', '')
        if application_deadline:
            position_data['jp_application_deadline'] = application_deadline.split(' ')[0]  # Keep only YYYY-MM-DD
        else:
            position_data['jp_application_deadline'] = ''

        # Extract locations
        locations = position.findall(".//location")
        if locations:
            position_data['country'] = locations[0].findtext('country', '')
            position_data['state'] = locations[0].findtext('state', '')
            position_data['city'] = locations[0].findtext('city', '')

        # Extract JEL Classifications
        jel_classifications = position.findall(".//jel_class")
        if jel_classifications:
            position_data['jel_code'] = jel_classifications[0].findtext('jc_code', '')
            position_data['jel_description'] = jel_classifications[0].findtext('jc_description', '')

        # Add position data to the list
        data.append(position_data)

    # Create a DataFrame from the extracted data
    return pd.DataFrame(data)

# Function to update the DataFrame with new positions and check for changes
def update_dataframe(existing_df, new_positions_df):
    # Merge the new positions with the existing DataFrame based on 'jp_id'
    updated_df = pd.merge(existing_df, new_positions_df, on='jp_id', how='outer', suffixes=('', '_new'))

    # Track rows that have changes
    changes = []

    # Check for differences and update the columns where new data exists
    for column in new_positions_df.columns:
        if column != 'jp_id':
            # Check for changes by comparing existing columns with new columns
            updated_df[f'changed_{column}'] = updated_df.apply(
                lambda row: pd.notnull(row[f'{column}_new']) and row[column] != row[f'{column}_new'], axis=1
            )
            
            # Update only the rows where there's a difference between old and new data
            updated_df[column] = updated_df.apply(
                lambda row: row[f'{column}_new'] if pd.notnull(row[f'{column}_new']) else row[column], axis=1
            )

            # Drop the new column after processing
            updated_df.drop(f'{column}_new', axis=1, inplace=True)
    
    # Determine which rows have any changes across any columns
    updated_df['has_changes'] = updated_df[[col for col in updated_df.columns if col.startswith('changed_')]].any(axis=1)

    # Add a 'last_updated' column with the current date only if there are changes
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    updated_df['last_updated'] = updated_df.apply(
        lambda row: current_date if row['has_changes'] else '', axis=1
    )

    # Drop the 'changed_' helper columns and 'has_changes'
    updated_df.drop([col for col in updated_df.columns if col.startswith('changed_')], axis=1, inplace=True)
    updated_df.drop('has_changes', axis=1, inplace=True)

    return updated_df

# Create a DataFrame
df_1 = extract_position_data(xml_path1)


# Optionally, save the updated DataFrame to a file
#df_1.to_csv('updated_positions.csv', index=False) # change your path


# You only care about certain type of positions like me? Here is the strings to cut based on the values of ["jp_section"]
"""    
US: Full-Time Academic (Permanent, Tenure Track or Tenured)

US: Other Academic (Visiting or Temporary)

US: Other Academic (Part-time or Adjunct)

International:Full-Time Academic (Permanent, Tenure Track or Tenured)

International: Other Academic (Visiting or Temporary)

International: Other Academic (Part-time or Adjunct)

Full-Time Nonacademic

Other Nonacademic (Temporary, Part-Time, Non-Salaried, Consulting, Etc.)
"""

############################ NEW POSITIONS? RUN THIS ############################ 
############################ NEW POSITIONS? RUN THIS ############################ 
############################ NEW POSITIONS? RUN THIS ############################ 



import datetime


# Extract data from the new XML file
new_positions_df = extract_position_data(xml_path_update)

# Update the existing DataFrame with the new positions and track changes
updated_df = update_dataframe(df_1, new_positions_df)

# The last updated columns gives the date in which you are updating the dataframe and there are any changes to the values of the other columns.
# For example, you are updating the xml file and the deadline for a position changed. The column last_pupdated will tell you that 
# today (the day you are updating) there is a change for that position in any column. Feeling cute, might code it better later...


# Optionally, save the updated DataFrame to a file
#updated_df.to_csv('updated_positions.csv', index=False)


# Since chances are we will be updating the file daily, keep a csv everytime you run this and then just read it with pandas and 
# go through the new positions part.




























################### DONT KNOW THE JEL CODES? CUZ NO ONE DOES... RUN THE PART BELOW TO HAVE A DICTIONARY WITH THEM





input_text = """ 
A General Economics and Teaching
 
A1 	General Economics
	A10 	General
	A11 	Role of Economics,  Role of Economists,  Market for Economists
	A12 	Relation of Economics to Other Disciplines
	A13 	Relation of Economics to Social Values
	A14 	Sociology of Economics
	A19 	Other
 
A2 	Economic Education and Teaching of Economics
	A20 	General
	A21 	Pre-college
	A22 	Undergraduate
	A23 	Graduate
	A29 	Other
 
A3 	Collective Works
	A30 	General
	A31 	Collected Writings of Individuals
	A32 	Collective Volumes
	A33 	Handbooks
	A39 	Other


B History of Economic Thought, Methodology, and Heterodox Approaches
 
	B00 	General
 
B1 	History of Economic Thought through 1925
	B10 	General
	B11 	Preclassical (Ancient, Medieval, Mercantilist, Physiocratic)
	B12 	Classical (includes Adam Smith)
	B13 	Neoclassical through 1925 (Austrian, Marshallian, Walrasian, Wicksellian)
	B14 	Socialist,  Marxist
	B15 	Historical,  Institutional,  Evolutionary
	B16 	Quantitative and Mathematical
	B17 	International Trade and Finance
	B19 	Other
 
B2 	History of Economic Thought since 1925
	B20 	General
	B21 	Microeconomics
	B22 	Macroeconomics
	B23 	Econometrics,  Quantitative and Mathematical Studies
	B24 	Socialist,  Marxist,  Sraffian
	B25 	Historical,  Institutional,  Evolutionary,  Austrian,  Stockholm School
	B26 	Financial Economics
	B27 	International Trade and Finance
	B29 	Other
 
B3 	History of Economic Thought: Individuals
	B30 	General
	B31 	Individuals
	B32 	Obituaries
 
B4 	Economic Methodology
	B40 	General
	B41 	Economic Methodology
	B49 	Other
 
B5 	Current Heterodox Approaches
	B50 	General
	B51 	Socialist,  Marxian,  Sraffian
	B52 	Historical,  Institutional,  Evolutionary,  Modern Monetary Theory
	B53 	Austrian
	B54 	Feminist Economics
	B55 	Social Economics
	B59 	Other


C Mathematical and Quantitative Methods
 
	C00 	General
	C01 	Econometrics
	C02 	Mathematical Methods
 
C1 	Econometric and Statistical Methods and Methodology: General
	C10 	General
	C11 	Bayesian Analysis: General
	C12 	Hypothesis Testing: General
	C13 	Estimation: General
	C14 	Semiparametric and Nonparametric Methods: General
	C15 	Statistical Simulation Methods: General
	C18 	Methodological Issues: General
	C19 	Other
 
C2 	Single Equation Models,  Single Variables
	C20 	General
	C21 	Cross-Sectional Models,  Spatial Models,  Treatment Effect Models,  Quantile Regressions
	C22 	Time-Series Models,  Dynamic Quantile Regressions,  Dynamic Treatment Effect Models,  Diffusion Processes
	C23 	Panel Data Models,  Spatio-temporal Models
	C24 	Truncated and Censored Models,  Switching Regression Models,  Threshold Regression Models
	C25 	Discrete Regression and Qualitative Choice Models,  Discrete Regressors,  Proportions,  Probabilities
	C26 	Instrumental Variables (IV) Estimation
	C29 	Other
 
C3 	Multiple or Simultaneous Equation Models,  Multiple Variables
	C30 	General
	C31 	Cross-Sectional Models,  Spatial Models,  Treatment Effect Models,  Quantile Regressions,  Social Interaction Models
	C32 	Time-Series Models,  Dynamic Quantile Regressions,  Dynamic Treatment Effect Models,  Diffusion Processes,  State Space Models
	C33 	Panel Data Models,  Spatio-temporal Models
	C34 	Truncated and Censored Models,  Switching Regression Models
	C35 	Discrete Regression and Qualitative Choice Models,  Discrete Regressors,  Proportions
	C36 	Instrumental Variables (IV) Estimation
	C38 	Classification Methods,  Cluster Analysis,  Principal Components,  Factor Models
	C39 	Other
 
C4 	Econometric and Statistical Methods: Special Topics
	C40 	General
	C41 	Duration Analysis,  Optimal Timing Strategies
	C43 	Index Numbers and Aggregation
	C44 	Operations Research,  Statistical Decision Theory
	C45 	Neural Networks and Related Topics
	C46 	Specific Distributions,  Specific Statistics
	C49 	Other
 
C5 	Econometric Modeling
	C50 	General
	C51 	Model Construction and Estimation
	C52 	Model Evaluation, Validation, and Selection
	C53 	Forecasting and Prediction Methods,  Simulation Methods
	C54 	Quantitative Policy Modeling
	C55 	Large Data Sets: Modeling and Analysis
	C57 	Econometrics of Games and Auctions
	C58 	Financial Econometrics
	C59 	Other
 
C6 	Mathematical Methods,  Programming Models,  Mathematical and Simulation Modeling
	C60 	General
	C61 	Optimization Techniques,  Programming Models,  Dynamic Analysis
	C62 	Existence and Stability Conditions of Equilibrium
	C63 	Computational Techniques,  Simulation Modeling
	C65 	Miscellaneous Mathematical Tools
	C67 	Input–Output Models
	C68 	Computable General Equilibrium Models
	C69 	Other
 
C7 	Game Theory and Bargaining Theory
	C70 	General
	C71 	Cooperative Games
	C72 	Noncooperative Games
	C73 	Stochastic and Dynamic Games,  Evolutionary Games,  Repeated Games
	C78 	Bargaining Theory,  Matching Theory
	C79 	Other
 
C8 	Data Collection and Data Estimation Methodology,  Computer Programs
	C80 	General
	C81 	Methodology for Collecting, Estimating, and Organizing Microeconomic Data,  Data Access
	C82 	Methodology for Collecting, Estimating, and Organizing Macroeconomic Data,  Data Access
	C83 	Survey Methods,  Sampling Methods
	C87 	Econometric Software
	C88 	Other Computer Software
	C89 	Other
 
C9 	Design of Experiments
	C90 	General
	C91 	Laboratory, Individual Behavior
	C92 	Laboratory, Group Behavior
	C93 	Field Experiments
	C99 	Other


D Microeconomics
 
	D00 	General
	D01 	Microeconomic Behavior: Underlying Principles
	D02 	Institutions: Design, Formation, Operations, and Impact
	D04 	Microeconomic Policy: Formulation, Implementation, and Evaluation
 
D1 	Household Behavior and Family Economics
	D10 	General
	D11 	Consumer Economics: Theory
	D12 	Consumer Economics: Empirical Analysis
	D13 	Household Production and Intrahousehold Allocation
	D14 	Household Saving,  Personal Finance
	D15 	Intertemporal Household Choice,  Life Cycle Models and Saving
	D16 	Collaborative Consumption
	D18 	Consumer Protection
	D19 	Other
 
D2 	Production and Organizations
	D20 	General
	D21 	Firm Behavior: Theory
	D22 	Firm Behavior: Empirical Analysis
	D23 	Organizational Behavior,  Transaction Costs,  Property Rights
	D24 	Production,  Cost,  Capital,  Capital, Total Factor, and Multifactor Productivity,  Capacity
	D25 	Intertemporal Firm Choice: Investment, Capacity, and Financing
	D26 	Crowd-Based Firms
	D29 	Other
 
D3 	Distribution
	D30 	General
	D31 	Personal Income, Wealth, and Their Distributions
	D33 	Factor Income Distribution
	D39 	Other
 
D4 	Market Structure, Pricing, and Design
	D40 	General
	D41 	Perfect Competition
	D42 	Monopoly
	D43 	Oligopoly and Other Forms of Market Imperfection
	D44 	Auctions
	D45 	Rationing,  Licensing
	D46 	Value Theory
	D47 	Market Design
	D49 	Other
 
D5 	General Equilibrium and Disequilibrium
	D50 	General
	D51 	Exchange and Production Economies
	D52 	Incomplete Markets
	D53 	Financial Markets
	D57 	Input–Output Tables and Analysis
	D58 	Computable and Other Applied General Equilibrium Models
	D59 	Other
 
D6 	Welfare Economics
	D60 	General
	D61 	Allocative Efficiency,  Cost–Benefit Analysis
	D62 	Externalities
	D63 	Equity, Justice, Inequality, and Other Normative Criteria and Measurement
	D64 	Altruism,  Philanthropy,  Intergenerational Transfers
	D69 	Other
 
D7 	Analysis of Collective Decision-Making
	D70 	General
	D71 	Social Choice,  Clubs,  Committees,  Associations
	D72 	Political Processes: Rent-Seeking, Lobbying, Elections, Legislatures, and Voting Behavior
	D73 	Bureaucracy,  Administrative Processes in Public Organizations,  Corruption
	D74 	Conflict,  Conflict Resolution,  Alliances,  Revolutions
	D78 	Positive Analysis of Policy Formulation and Implementation
	D79 	Other
 
D8 	Information, Knowledge, and Uncertainty
	D80 	General
	D81 	Criteria for Decision-Making under Risk and Uncertainty
	D82 	Asymmetric and Private Information,  Mechanism Design
	D83 	Search,  Learning,  Information and Knowledge,  Communication,  Belief,  Unawareness
	D84 	Expectations,  Speculations
	D85 	Network Formation and Analysis: Theory
	D86 	Economics of Contract: Theory
	D87 	Neuroeconomics
	D89 	Other
 
D9 	Micro-Based Behavioral Economics
	D90 	General
	D91 	Role and Effects of Psychological, Emotional, Social, and Cognitive Factors on Decision Making


E Macroeconomics and Monetary Economics
 
	E00 	General
	E01 	Measurement and Data on National Income and Product Accounts and Wealth,  Environmental Accounts
	E02 	Institutions and the Macroeconomy
 
E1 	General Aggregative Models
	E10 	General
	E11 	Marxian,  Sraffian,  Kaleckian
	E12 	Keynes,  Keynesian,  Post-Keynesian,  Modern Monetary Theory
	E13 	Neoclassical
	E14 	Austrian,  Evolutionary,  Institutional
	E16 	Social Accounting Matrix
	E17 	Forecasting and Simulation: Models and Applications
	E19 	Other
 
E2 	Consumption, Saving, Production, Investment, Labor Markets, and Informal Economy
	E20 	General
	E21 	Consumption,  Saving,  Wealth
	E22 	Investment,  Capital,  Intangible Capital,  Capacity
	E23 	Production
	E24 	Employment,  Unemployment,  Wages,  Intergenerational Income Distribution,  Aggregate Human Capital,  Aggregate Labor Productivity
	E25 	Aggregate Factor Income Distribution
	E26 	Informal Economy,  Underground Economy
	E27 	Forecasting and Simulation: Models and Applications
	E29 	Other
 
E3 	Prices, Business Fluctuations, and Cycles
	E30 	General
	E31 	Price Level,  Inflation,  Deflation
	E32 	Business Fluctuations,  Cycles
	E37 	Forecasting and Simulation: Models and Applications
	E39 	Other
 
E4 	Money and Interest Rates
	E40 	General
	E41 	Demand for Money
	E42 	Monetary Systems,  Standards,  Regimes,  Government and the Monetary System,  Payment Systems
	E43 	Interest Rates: Determination, Term Structure, and Effects
	E44 	Financial Markets and the Macroeconomy
	E47 	Forecasting and Simulation: Models and Applications
	E49 	Other
 
E5 	Monetary Policy, Central Banking, and the Supply of Money and Credit
	E50 	General
	E51 	Money Supply,  Credit,  Money Multipliers
	E52 	Monetary Policy
	E58 	Central Banks and Their Policies
	E59 	Other
 
E6 	Macroeconomic Policy, Macroeconomic Aspects of Public Finance, and General Outlook
	E60 	General
	E61 	Policy Objectives,  Policy Designs and Consistency,  Policy Coordination
	E62 	Fiscal Policy,  Modern Monetary Theory
	E63 	Comparative or Joint Analysis of Fiscal and Monetary Policy,  Stabilization,  Treasury Policy
	E64 	Incomes Policy,  Price Policy
	E65 	Studies of Particular Policy Episodes
	E66 	General Outlook and Conditions
	E69 	Other
 
E7 	Macro-Based Behavioral Economics
	E70 	General
	E71 	Role and Effects of Psychological, Emotional, Social, and Cognitive Factors on the Macro Economy


F International Economics
 
	F00 	General
	F01 	Global Outlook
	F02 	International Economic Order and Integration
 
F1 	Trade
	F10 	General
	F11 	Neoclassical Models of Trade
	F12 	Models of Trade with Imperfect Competition and Scale Economies,  Fragmentation
	F13 	Trade Policy,  International Trade Organizations
	F14 	Empirical Studies of Trade
	F15 	Economic Integration
	F16 	Trade and Labor Market Interactions
	F17 	Trade Forecasting and Simulation
	F18 	Trade and Environment
	F19 	Other
 
F2 	International Factor Movements and International Business
	F20 	General
	F21 	International Investment,  Long-Term Capital Movements
	F22 	International Migration
	F23 	Multinational Firms,  International Business
	F24 	Remittances
	F29 	Other
 
F3 	International Finance
	F30 	General
	F31 	Foreign Exchange
	F32 	Current Account Adjustment,  Short-Term Capital Movements
	F33 	International Monetary Arrangements and Institutions
	F34 	International Lending and Debt Problems
	F35 	Foreign Aid
	F36 	Financial Aspects of Economic Integration
	F37 	International Finance Forecasting and Simulation: Models and Applications
	F38 	International Financial Policy: Financial Transactions Tax; Capital Controls
	F39 	Other
 
F4 	Macroeconomic Aspects of International Trade and Finance
	F40 	General
	F41 	Open Economy Macroeconomics
	F42 	International Policy Coordination and Transmission
	F43 	Economic Growth of Open Economies
	F44 	International Business Cycles
	F45 	Macroeconomic Issues of Monetary Unions
	F47 	Forecasting and Simulation: Models and Applications
	F49 	Other
 
F5 	International Relations, National Security, and International Political Economy
	F50 	General
	F51 	International Conflicts,  Negotiations,  Sanctions
	F52 	National Security,  Economic Nationalism
	F53 	International Agreements and Observance,  International Organizations
	F54 	Colonialism,  Imperialism,  Postcolonialism
	F55 	International Institutional Arrangements
	F59 	Other
 
F6 	Economic Impacts of Globalization
	F60 	General
	F61 	Microeconomic Impacts
	F62 	Macroeconomic Impacts
	F63 	Economic Development
	F64 	Environment
	F65 	Finance
	F66 	Labor
	F68 	Policy
	F69 	Other


G Financial Economics
 
	G00 	General
	G01 	Financial Crises
 
G1 	General Financial Markets
	G10 	General
	G11 	Portfolio Choice,  Investment Decisions
	G12 	Asset Pricing,  Trading Volume,  Bond Interest Rates
	G13 	Contingent Pricing,  Futures Pricing
	G14 	Information and Market Efficiency,  Event Studies,  Insider Trading
	G15 	International Financial Markets
	G17 	Financial Forecasting and Simulation
	G18 	Government Policy and Regulation
	G19 	Other
 
G2 	Financial Institutions and Services
	G20 	General
	G21 	Banks,  Depository Institutions,  Micro Finance Institutions,  Mortgages
	G22 	Insurance,  Insurance Companies,  Actuarial Studies
	G23 	Non-bank Financial Institutions,  Financial Instruments,  Institutional Investors
	G24 	Investment Banking,  Venture Capital,  Brokerage,  Ratings and Ratings Agencies
	G28 	Government Policy and Regulation
	G29 	Other
 
G3 	Corporate Finance and Governance
	G30 	General
	G31 	Capital Budgeting,  Fixed Investment and Inventory Studies,  Capacity
	G32 	Financing Policy,  Financial Risk and Risk Management,  Capital and Ownership Structure,  Value of Firms,  Goodwill
	G33 	Bankruptcy,  Liquidation
	G34 	Mergers,  Acquisitions,  Restructuring,  Corporate Governance
	G35 	Payout Policy
	G38 	Government Policy and Regulation
	G39 	Other
 
G4 	Behavioral Finance
	G40 	General
	G41 	Role and Effects of Psychological, Emotional, Social, and Cognitive Factors on Decision Making in Financial Markets
 
G5 	Household Finance
	G50 	General
	G51 	Household Saving, Borrowing, Debt, and Wealth
	G52 	Insurance
	G53 	Financial Literacy
	G59 	Other


H Public Economics
 
	H00 	General
 
H1 	Structure and Scope of Government
	H10 	General
	H11 	Structure, Scope, and Performance of Government
	H12 	Crisis Management
	H13 	Economics of Eminent Domain,  Expropriation,  Nationalization
	H19 	Other
 
H2 	Taxation, Subsidies, and Revenue
	H20 	General
	H21 	Efficiency,  Optimal Taxation
	H22 	Incidence
	H23 	Externalities,  Redistributive Effects,  Environmental Taxes and Subsidies
	H24 	Personal Income and Other Nonbusiness Taxes and Subsidies
	H25 	Business Taxes and Subsidies
	H26 	Tax Evasion and Avoidance
	H27 	Other Sources of Revenue
	H29 	Other
 
H3 	Fiscal Policies and Behavior of Economic Agents
	H30 	General
	H31 	Household
	H32 	Firm
	H39 	Other
 
H4 	Publicly Provided Goods
	H40 	General
	H41 	Public Goods
	H42 	Publicly Provided Private Goods
	H43 	Project Evaluation,  Social Discount Rate
	H44 	Publicly Provided Goods: Mixed Markets
	H49 	Other
 
H5 	National Government Expenditures and Related Policies
	H50 	General
	H51 	Government Expenditures and Health
	H52 	Government Expenditures and Education
	H53 	Government Expenditures and Welfare Programs
	H54 	Infrastructures,  Other Public Investment and Capital Stock
	H55 	Social Security and Public Pensions
	H56 	National Security and War
	H57 	Procurement
	H59 	Other
 
H6 	National Budget, Deficit, and Debt
	H60 	General
	H61 	Budget,  Budget Systems
	H62 	Deficit,  Surplus
	H63 	Debt,  Debt Management,  Sovereign Debt
	H68 	Forecasts of Budgets, Deficits, and Debt
	H69 	Other
 
H7 	State and Local Government,  Intergovernmental Relations
	H70 	General
	H71 	State and Local Taxation, Subsidies, and Revenue
	H72 	State and Local Budget and Expenditures
	H73 	Interjurisdictional Differentials and Their Effects
	H74 	State and Local Borrowing
	H75 	State and Local Government: Health,  Education,  Welfare,  Public Pensions
	H76 	State and Local Government: Other Expenditure Categories
	H77 	Intergovernmental Relations,  Federalism,  Secession
	H79 	Other
 
H8 	Miscellaneous Issues
	H80 	General
	H81 	Governmental Loans,  Loan Guarantees,  Credits,  Grants,  Bailouts
	H82 	Governmental Property
	H83 	Public Administration,  Public Sector Accounting and Audits
	H84 	Disaster Aid
	H87 	International Fiscal Issues,  International Public Goods
	H89 	Other


I Health, Education, and Welfare
 
	I00 	General
 
I1 	Health
	I10 	General
	I11 	Analysis of Health Care Markets
	I12 	Health Behavior
	I13 	Health Insurance, Public and Private
	I14 	Health and Inequality
	I15 	Health and Economic Development
	I18 	Government Policy,  Regulation,  Public Health
	I19 	Other
 
I2 	Education and Research Institutions
	I20 	General
	I21 	Analysis of Education
	I22 	Educational Finance,  Financial Aid
	I23 	Higher Education,  Research Institutions
	I24 	Education and Inequality
	I25 	Education and Economic Development
	I26 	Returns to Education
	I28 	Government Policy
	I29 	Other
 
I3 	Welfare, Well-Being, and Poverty
	I30 	General
	I31 	General Welfare, Well-Being
	I32 	Measurement and Analysis of Poverty
	I38 	Government Policy,  Provision and Effects of Welfare Programs
	I39 	Other


J Labor and Demographic Economics
 
	J00 	General
	J01 	Labor Economics: General
	J08 	Labor Economics Policies
 
J1 	Demographic Economics
	J10 	General
	J11 	Demographic Trends, Macroeconomic Effects, and Forecasts
	J12 	Marriage,  Marital Dissolution,  Family Structure,  Domestic Abuse
	J13 	Fertility,  Family Planning,  Child Care,  Children,  Youth
	J14 	Economics of the Elderly,  Economics of Disability,  Non-Labor Market Discrimination†
	J15 	Economics of Minorities, Races, Indigenous Peoples, and Immigrants,  Non-labor Discrimination
	J16 	Economics of Gender,  Non-labor Discrimination
	J17 	Value of Life,  Forgone Income
	J18 	Public Policy
	J19 	Other
 
J2 	Demand and Supply of Labor
	J20 	General
	J21 	Labor Force and Employment, Size, and Structure
	J22 	Time Allocation and Labor Supply
	J23 	Labor Demand
	J24 	Human Capital,  Skills,  Occupational Choice,  Labor Productivity
	J26 	Retirement,  Retirement Policies
	J28 	Safety,  Job Satisfaction,  Related Public Policy
	J29 	Other
 
J3 	Wages, Compensation, and Labor Costs
	J30 	General
	J31 	Wage Level and Structure,  Wage Differentials
	J32 	Nonwage Labor Costs and Benefits,  Retirement Plans,  Private Pensions
	J33 	Compensation Packages,  Payment Methods
	J38 	Public Policy
	J39 	Other
 
J4 	Particular Labor Markets
	J40 	General
	J41 	Labor Contracts
	J42 	Monopsony,  Segmented Labor Markets
	J43 	Agricultural Labor Markets
	J44 	Professional Labor Markets,  Occupational Licensing
	J45 	Public Sector Labor Markets
	J46 	Informal Labor Markets
	J47 	Coercive Labor Markets
	J48 	Public Policy
	J49 	Other
 
J5 	Labor–Management Relations, Trade Unions, and Collective Bargaining
	J50 	General
	J51 	Trade Unions: Objectives, Structure, and Effects
	J52 	Dispute Resolution: Strikes, Arbitration, and Mediation,  Collective Bargaining
	J53 	Labor–Management Relations,  Industrial Jurisprudence
	J54 	Producer Cooperatives,  Labor Managed Firms,  Employee Ownership
	J58 	Public Policy
	J59 	Other
 
J6 	Mobility, Unemployment, Vacancies, and Immigrant Workers
	J60 	General
	J61 	Geographic Labor Mobility,  Immigrant Workers
	J62 	Job, Occupational, and Intergenerational Mobility
	J63 	Turnover,  Vacancies,  Layoffs
	J64 	Unemployment: Models, Duration, Incidence, and Job Search
	J65 	Unemployment Insurance,  Severance Pay,  Plant Closings
	J68 	Public Policy
	J69 	Other
 
J7 	Labor Discrimination
	J70 	General
	J71 	Discrimination
	J78 	Public Policy
	J79 	Other
 
J8 	Labor Standards: National and International
	J80 	General
	J81 	Working Conditions
	J82 	Labor Force Composition
	J83 	Workers' Rights
	J88 	Public Policy
	J89 	Other


K Law and Economics
 
	K00 	General
 
K1 	Basic Areas of Law
	K10 	General
	K11 	Property Law
	K12 	Contract Law
	K13 	Tort Law and Product Liability,  Forensic Economics
	K14 	Criminal Law
	K15 	Civil Law,  Common Law
	K16 	Election Law
	K19 	Other
 
K2 	Regulation and Business Law
	K20 	General
	K21 	Antitrust Law
	K22 	Business and Securities Law
	K23 	Regulated Industries and Administrative Law
	K24 	Cyber Law
	K25 	Real Estate Law
	K29 	Other
 
K3 	Other Substantive Areas of Law
	K30 	General
	K31 	Labor Law
	K32 	Energy, Environmental, Health, and Safety Law
	K33 	International Law
	K34 	Tax Law
	K35 	Personal Bankruptcy Law
	K36 	Family and Personal Law
	K37 	Immigration Law
	K38 	Human Rights Law,  Gender Law,  Animal Rights Law
	K39 	Other
 
K4 	Legal Procedure, the Legal System, and Illegal Behavior
	K40 	General
	K41 	Litigation Process
	K42 	Illegal Behavior and the Enforcement of Law
	K49 	Other


L Industrial Organization
 
	L00 	General
 
L1 	Market Structure, Firm Strategy, and Market Performance
	L10 	General
	L11 	Production, Pricing, and Market Structure,  Size Distribution of Firms
	L12 	Monopoly,  Monopolization Strategies
	L13 	Oligopoly and Other Imperfect Markets
	L14 	Transactional Relationships,  Contracts and Reputation,  Networks
	L15 	Information and Product Quality,  Standardization and Compatibility
	L16 	Industrial Organization and Macroeconomics: Industrial Structure and Structural Change,  Industrial Price Indices
	L17 	Open Source Products and Markets
	L19 	Other
 
L2 	Firm Objectives, Organization, and Behavior
	L20 	General
	L21 	Business Objectives of the Firm
	L22 	Firm Organization and Market Structure
	L23 	Organization of Production
	L24 	Contracting Out,  Joint Ventures,  Technology Licensing
	L25 	Firm Performance: Size, Diversification, and Scope
	L26 	Entrepreneurship
	L29 	Other
 
L3 	Nonprofit Organizations and Public Enterprise
	L30 	General
	L31 	Nonprofit Institutions,  NGOs,  Social Entrepreneurship
	L32 	Public Enterprises,  Public-Private Enterprises
	L33 	Comparison of Public and Private Enterprises and Nonprofit Institutions,  Privatization,  Contracting Out
	L38 	Public Policy
	L39 	Other
 
L4 	Antitrust Issues and Policies
	L40 	General
	L41 	Monopolization,  Horizontal Anticompetitive Practices
	L42 	Vertical Restraints,  Resale Price Maintenance,  Quantity Discounts
	L43 	Legal Monopolies and Regulation or Deregulation
	L44 	Antitrust Policy and Public Enterprises, Nonprofit Institutions, and Professional Organizations
	L49 	Other
 
L5 	Regulation and Industrial Policy
	L50 	General
	L51 	Economics of Regulation
	L52 	Industrial Policy,  Sectoral Planning Methods
	L53 	Enterprise Policy
	L59 	Other
 
L6 	Industry Studies: Manufacturing
	L60 	General
	L61 	Metals and Metal Products,  Cement,  Glass,  Ceramics
	L62 	Automobiles,  Other Transportation Equipment,  Related Parts and Equipment
	L63 	Microelectronics,  Computers,  Communications Equipment
	L64 	Other Machinery,  Business Equipment,  Armaments
	L65 	Chemicals,  Rubber,  Drugs,  Biotechnology,  Plastics
	L66 	Food,  Beverages,  Cosmetics,  Tobacco,  Wine and Spirits
	L67 	Other Consumer Nondurables: Clothing, Textiles, Shoes, and Leather Goods; Household Goods; Sports Equipment
	L68 	Appliances,  Furniture,  Other Consumer Durables
	L69 	Other
 
L7 	Industry Studies: Primary Products and Construction
	L70 	General
	L71 	Mining, Extraction, and Refining: Hydrocarbon Fuels
	L72 	Mining, Extraction, and Refining: Other Nonrenewable Resources
	L73 	Forest Products
	L74 	Construction
	L78 	Government Policy
	L79 	Other
 
L8 	Industry Studies: Services
	L80 	General
	L81 	Retail and Wholesale Trade,  e-Commerce
	L82 	Entertainment,  Media
	L83 	Sports,  Gambling,  Restaurants,  Recreation,  Tourism
	L84 	Personal, Professional, and Business Services
	L85 	Real Estate Services
	L86 	Information and Internet Services,  Computer Software
	L87 	Postal and Delivery Services
	L88 	Government Policy
	L89 	Other
 
L9 	Industry Studies: Transportation and Utilities
	L90 	General
	L91 	Transportation: General
	L92 	Railroads and Other Surface Transportation
	L93 	Air Transportation
	L94 	Electric Utilities
	L95 	Gas Utilities,  Pipelines,  Water Utilities
	L96 	Telecommunications
	L97 	Utilities: General
	L98 	Government Policy
	L99 	Other


M Business Administration and Business Economics,  Marketing,  Accounting,  Personnel Economics
 
	M00 	General
 
M1 	Business Administration
	M10 	General
	M11 	Production Management
	M12 	Personnel Management,  Executives; Executive Compensation
	M13 	New Firms,  Startups
	M14 	Corporate Culture,  Diversity,  Social Responsibility
	M15 	IT Management
	M16 	International Business Administration
	M19 	Other
 
M2 	Business Economics
	M20 	General
	M21 	Business Economics
	M29 	Other
 
M3 	Marketing and Advertising
	M30 	General
	M31 	Marketing
	M37 	Advertising
	M38 	Government Policy and Regulation
	M39 	Other
 
M4 	Accounting and Auditing
	M40 	General
	M41 	Accounting
	M42 	Auditing
	M48 	Government Policy and Regulation
	M49 	Other
 
M5 	Personnel Economics
	M50 	General
	M51 	Firm Employment Decisions,  Promotions
	M52 	Compensation and Compensation Methods and Their Effects
	M53 	Training
	M54 	Labor Management
	M55 	Labor Contracting Devices
	M59 	Other


N Economic History
 
	N00 	General
	N01 	Development of the Discipline: Historiographical; Sources and Methods
 
N1 	Macroeconomics and Monetary Economics,  Industrial Structure,  Growth,  Fluctuations
	N10 	General, International, or Comparative
	N11 	US,  Canada: Pre-1913
	N12 	US,  Canada: 1913–
	N13 	Europe: Pre-1913
	N14 	Europe: 1913–
	N15 	Asia including Middle East
	N16 	Latin America,  Caribbean
	N17 	Africa,  Oceania
 
N2 	Financial Markets and Institutions
	N20 	General, International, or Comparative
	N21 	US,  Canada: Pre-1913
	N22 	US,  Canada: 1913–
	N23 	Europe: Pre-1913
	N24 	Europe: 1913–
	N25 	Asia including Middle East
	N26 	Latin America,  Caribbean
	N27 	Africa,  Oceania
 
N3 	Labor and Consumers, Demography, Education, Health, Welfare, Income, Wealth, Religion, and Philanthropy
	N30 	General, International, or Comparative
	N31 	US,  Canada: Pre-1913
	N32 	US,  Canada: 1913-
	N33 	Europe: Pre-1913
	N34 	Europe: 1913-
	N35 	Asia including Middle East
	N36 	Latin America,  Caribbean
	N37 	Africa,  Oceania
 
N4 	Government, War, Law, International Relations, and Regulation
	N40 	General, International, or Comparative
	N41 	US,  Canada: Pre-1913
	N42 	US,  Canada: 1913–
	N43 	Europe: Pre-1913
	N44 	Europe: 1913–
	N45 	Asia including Middle East
	N46 	Latin America,  Caribbean
	N47 	Africa,  Oceania
 
N5 	Agriculture, Natural Resources, Environment, and Extractive Industries
	N50 	General, International, or Comparative
	N51 	US,  Canada: Pre-1913
	N52 	US,  Canada: 1913–
	N53 	Europe: Pre-1913
	N54 	Europe: 1913–
	N55 	Asia including Middle East
	N56 	Latin America,  Caribbean
	N57 	Africa,  Oceania
 
N6 	Manufacturing and Construction
	N60 	General, International, or Comparative
	N61 	US,  Canada: Pre-1913
	N62 	US,  Canada: 1913–
	N63 	Europe: Pre-1913
	N64 	Europe: 1913–
	N65 	Asia including Middle East
	N66 	Latin America,  Caribbean
	N67 	Africa,  Oceania
 
N7 	Transport, Trade, Energy, Technology, and Other Services
	N70 	General, International, or Comparative
	N71 	US,  Canada: Pre-1913
	N72 	US,  Canada: 1913–
	N73 	Europe: Pre-1913
	N74 	Europe: 1913–
	N75 	Asia including Middle East
	N76 	Latin America,  Caribbean
	N77 	Africa,  Oceania
 
N8 	Micro-Business History
	N80 	General, International, or Comparative
	N81 	US,  Canada: Pre-1913
	N82 	US,  Canada: 1913–
	N83 	Europe: Pre-1913
	N84 	Europe: 1913–
	N85 	Asia including Middle East
	N86 	Latin America,  Caribbean
	N87 	Africa,  Oceania
 
N9 	Regional and Urban History
	N90 	General, International, or Comparative
	N91 	US,  Canada: Pre-1913
	N92 	US,  Canada: 1913–
	N93 	Europe: Pre-1913
	N94 	Europe: 1913–
	N95 	Asia including Middle East
	N96 	Latin America,  Caribbean
	N97 	Africa,  Oceania


O Economic Development, Innovation, Technological Change, and Growth
 
O1 	Economic Development
	O10 	General
	O11 	Macroeconomic Analyses of Economic Development
	O12 	Microeconomic Analyses of Economic Development
	O13 	Agriculture,  Natural Resources,  Energy,  Environment,  Other Primary Products
	O14 	Industrialization,  Manufacturing and Service Industries,  Choice of Technology
	O15 	Human Resources,  Human Development,  Income Distribution,  Migration
	O16 	Financial Markets,  Saving and Capital Investment,  Corporate Finance and Governance
	O17 	Formal and Informal Sectors,  Shadow Economy,  Institutional Arrangements
	O18 	Urban, Rural, Regional, and Transportation Analysis,  Housing,  Infrastructure
	O19 	International Linkages to Development,  Role of International Organizations
 
O2 	Development Planning and Policy
	O20 	General
	O21 	Planning Models,  Planning Policy
	O22 	Project Analysis
	O23 	Fiscal and Monetary Policy in Development
	O24 	Trade Policy,  Factor Movement Policy,  Foreign Exchange Policy
	O25 	Industrial Policy
	O29 	Other
 
O3 	Innovation,  Research and Development,  Technological Change,  Intellectual Property Rights
	O30 	General
	O31 	Innovation and Invention: Processes and Incentives
	O32 	Management of Technological Innovation and R&D
	O33 	Technological Change: Choices and Consequences,  Diffusion Processes
	O34 	Intellectual Property and Intellectual Capital
	O35 	Social Innovation
	O36 	Open Innovation
	O38 	Government Policy
	O39 	Other
 
O4 	Economic Growth and Aggregate Productivity
	O40 	General
	O41 	One, Two, and Multisector Growth Models
	O42 	Monetary Growth Models
	O43 	Institutions and Growth
	O44 	Environment and Growth
	O47 	Empirical Studies of Economic Growth,  Aggregate Productivity,  Cross-Country Output Convergence
	O49 	Other
 
O5 	Economywide Country Studies
	O50 	General
	O51 	US,  Canada
	O52 	Europe
	O53 	Asia including Middle East
	O54 	Latin America,  Caribbean
	O55 	Africa
	O56 	Oceania
	O57 	Comparative Studies of Countries


P Political Economy and Comparative Economic Systems
 
	P00 	General
 
P1 	Capitalist Economies
	P10 	General
	P11 	Planning, Coordination, and Reform
	P12 	Capitalist Enterprises
	P13 	Cooperative Enterprises
	P14 	Property Rights
	P16 	Capitalist Institutions,  Welfare State
	P17 	Performance and Prospects
	P18 	Energy,  Environment
	P19 	Other
 
P2 	Socialist and Transition Economies
	P20 	General
	P21 	Planning, Coordination, and Reform
	P22 	Prices
	P23 	Factor and Product Markets,  Industry Studies,  Population
	P24 	National Income, Product, and Expenditure,  Money,  Inflation
	P25 	Urban, Rural, and Regional Economics
	P26 	Property Rights
	P27 	Performance and Prospects
	P28 	Natural Resources,  Energy,  Environment
	P29 	Other
 
P3 	Socialist Institutions and Their Transitions
	P30 	General
	P31 	Socialist Enterprises and Their Transitions
	P32 	Collectives,  Communes,  Agriculture
	P33 	International Trade, Finance, Investment, Relations, and Aid
	P34 	Financial Economics
	P35 	Public Economics
	P36 	Consumer Economics,  Health,  Education and Training,  Welfare, Income, Wealth, and Poverty
	P37 	Legal Institutions,  Illegal Behavior
	P39 	Other
 
P4 	Other Economic Systems
	P40 	General
	P41 	Planning, Coordination, and Reform
	P42 	Productive Enterprises,  Factor and Product Markets,  Prices,  Population
	P43 	Public Economics,  Financial Economics
	P44 	National Income, Product, and Expenditure,  Money,  Inflation
	P45 	International Trade, Finance, Investment, and Aid
	P46 	Consumer Economics,  Health,  Education and Training,  Welfare, Income, Wealth, and Poverty
	P47 	Performance and Prospects
	P48 	Legal Institutions,  Property Rights,  Natural Resources,  Energy,  Environment,  Regional Studies
	P49 	Other
 
P5 	Comparative Economic Systems
	P50 	General
	P51 	Comparative Analysis of Economic Systems
	P52 	Comparative Studies of Particular Economies
	P59 	Other


Q Agricultural and Natural Resource Economics,  Environmental and Ecological Economics
 
	Q00 	General
	Q01 	Sustainable Development
	Q02 	Commodity Markets
 
Q1 	Agriculture
	Q10 	General
	Q11 	Aggregate Supply and Demand Analysis,  Prices
	Q12 	Micro Analysis of Farm Firms, Farm Households, and Farm Input Markets
	Q13 	Agricultural Markets and Marketing,  Cooperatives,  Agribusiness
	Q14 	Agricultural Finance
	Q15 	Land Ownership and Tenure,  Land Reform,  Land Use,  Irrigation,  Agriculture and Environment
	Q16 	R&D,  Agricultural Technology,  Biofuels,  Agricultural Extension Services
	Q17 	Agriculture in International Trade
	Q18 	Agricultural Policy,  Food Policy,  Animal Welfare Policy
	Q19 	Other
 
Q2 	Renewable Resources and Conservation
	Q20 	General
	Q21 	Demand and Supply,  Prices
	Q22 	Fishery,  Aquaculture
	Q23 	Forestry
	Q24 	Land
	Q25 	Water
	Q26 	Recreational Aspects of Natural Resources
	Q27 	Issues in International Trade
	Q28 	Government Policy
	Q29 	Other
 
Q3 	Nonrenewable Resources and Conservation
	Q30 	General
	Q31 	Demand and Supply,  Prices
	Q32 	Exhaustible Resources and Economic Development
	Q33 	Resource Booms
	Q34 	Natural Resources and Domestic and International Conflicts
	Q35 	Hydrocarbon Resources
	Q37 	Issues in International Trade
	Q38 	Government Policy
	Q39 	Other
 
Q4 	Energy
	Q40 	General
	Q41 	Demand and Supply,  Prices
	Q42 	Alternative Energy Sources
	Q43 	Energy and the Macroeconomy
	Q47 	Energy Forecasting
	Q48 	Government Policy
	Q49 	Other
 
Q5 	Environmental Economics
	Q50 	General
	Q51 	Valuation of Environmental Effects
	Q52 	Pollution Control Adoption and Costs,  Distributional Effects,  Employment Effects
	Q53 	Air Pollution,  Water Pollution,  Noise,  Hazardous Waste,  Solid Waste,  Recycling
	Q54 	Climate,  Natural Disasters and Their Management,  Global Warming
	Q55 	Technological Innovation
	Q56 	Environment and Development,  Environment and Trade,  Sustainability,  Environmental Accounts and Accounting,  Environmental Equity,  Population Growth
	Q57 	Ecological Economics: Ecosystem Services,  Biodiversity Conservation,  Bioeconomics,  Industrial Ecology
	Q58 	Government Policy
	Q59 	Other


R Urban, Rural, Regional, Real Estate, and Transportation Economics
 
	R00 	General
 
R1 	General Regional Economics
	R10 	General
	R11 	Regional Economic Activity: Growth, Development, Environmental Issues, and Changes
	R12 	Size and Spatial Distributions of Regional Economic Activity
	R13 	General Equilibrium and Welfare Economic Analysis of Regional Economies
	R14 	Land Use Patterns
	R15 	Econometric and Input–Output Models,  Other Models
	R19 	Other
 
R2 	Household Analysis
	R20 	General
	R21 	Housing Demand
	R22 	Other Demand
	R23 	Regional Migration,  Regional Labor Markets,  Population,  Neighborhood Characteristics
	R28 	Government Policy
	R29 	Other
 
R3 	Real Estate Markets, Spatial Production Analysis, and Firm Location
	R30 	General
	R31 	Housing Supply and Markets
	R32 	Other Spatial Production and Pricing Analysis
	R33 	Nonagricultural and Nonresidential Real Estate Markets
	R38 	Government Policy
	R39 	Other
 
R4 	Transportation Economics
	R40 	General
	R41 	Transportation: Demand, Supply, and Congestion,  Travel Time,  Safety and Accidents,  Transportation Noise
	R42 	Government and Private Investment Analysis,  Road Maintenance,  Transportation Planning
	R48 	Government Pricing and Policy
	R49 	Other
 
R5 	Regional Government Analysis
	R50 	General
	R51 	Finance in Urban and Rural Economies
	R52 	Land Use and Other Regulations
	R53 	Public Facility Location Analysis,  Public Investment and Capital Stock
	R58 	Regional Development Planning and Policy
	R59 	Other


Y Miscellaneous Categories
 
Y1 	Data: Tables and Charts
	Y10 	Data: Tables and Charts
 
Y2 	Introductory Material
	Y20 	Introductory Material
 
Y3 	Book Reviews (unclassified)
	Y30 	Book Reviews (unclassified)
 
Y4 	Dissertations (unclassified)
	Y40 	Dissertations (unclassified)
 
Y5 	Further Reading (unclassified)
	Y50 	Further Reading (unclassified)
 
Y6 	Excerpts
	Y60 	Excerpts
 
Y7 	No Author General Discussions
	Y70 	No Author General Discussions
 
Y8 	Related Disciplines
	Y80 	Related Disciplines
 
Y9 	Other
	Y90 	Other
	Y91 	Pictures and Maps
	Y92 	Novels, Self-Help Books, etc


Z Other Special Topics
 
	Z00 	General
 
Z1 	Cultural Economics,  Economic Sociology,  Economic Anthropology
	Z10 	General
	Z11 	Economics of the Arts and Literature
	Z12 	Religion
	Z13 	Economic Sociology,  Economic Anthropology,  Language,  Social and Economic Stratification
	Z18 	Public Policy
	Z19 	Other
 
Z2 	Sports Economics
	Z20 	General
	Z21 	Industry Studies
	Z22 	Labor Issues
	Z23 	Finance
	Z28 	Policy
	Z29 	Other
 
Z3 	Tourism Economics
	Z30 	General
	Z31 	Industry Studies
	Z32 	Tourism and Development
	Z33 	Marketing and Finance
	Z38 	Policy
	Z39 	Other

 """
 
 

# Initialize an empty dictionary
JELcodes = {}

# Split the input text into lines
lines = input_text.splitlines()

# Regular expression to match keys with strings followed by numbers (e.g., A1, B10)
pattern = re.compile(r"^([A-Z]+\d{1,2})\s+(.+)$")

# Iterate over each line
for line in lines:
    match = pattern.match(line)
    if match:
        # Extract the key and the value from the line
        key = match.group(1)
        value = match.group(2).strip()
        # Add the key-value pair to the dictionary
        JELcodes[key] = value