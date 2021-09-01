# AIIDE21 Artifact - Optimizing Profit by Mitigating Recurrent Churn Labeling Issues: Analysis from the Game Domain
The datasets, codes, and results for the AIIDE21 accepted paper: "Optimizing Profit by Mitigating Recurrent Churn Labeling Issues: Analysis from the Game Domain".

# Problem
  This paper mitigates recurrent issues when labeling players as churners. 
  
  It tackles two main issues:
  
    1- Players are labeled using the behavior of the whole player base;
    2- The definition of churn (i.e., what can be considered as churn) is static; 

# Solution
  We proposed a novel metric to define churn individually (named Individual Fixed Value) and a novel evaluation metric (named Churn Definition Change Rate) that can be used as a warning that the definition should be updated and the churn classifier should be retrained.

# GitHub Objective
  This project aims to validate the paper's findings and can be used to understand how to implement the proposed solution in a production environment.

# Software Requirement:
  The only requirement is Python 3.X.

# Hardware Requirements:
  The hardware requirement can vary depending on your goal and input data. 
  It is advisable to have 32 GB of RAM to run the experiments because it considers numerous windows sizes and slides them throughout the whole dataset. 
  To implement in a production environment, the requirement depends on the input data, but it should be much smaller.

# Warning
  Since there are numerous windows sizes and all of them run through the whole dataset, the number of iterations is very high. 
  In an AMD Ryzen 9 5950X it took three and a half hours to run it all.
 
# Datasets Information
  The datasets used in the paper and provided in this project contain the login information of multiple players in a certain period. More information can be seen below:

  Game | # Player | # Months | Period
  --- | --- | --- | ---
  LOL | 2400 | 23 | Oct. 2018 - Sep. 2020
  WOW | 91064 | 37 | Jan. 2006 - Jan. 2009

# Input Data Information
  If you want to test with your own data, the input file should be a CSV without a header, delimited by ',' (the delimiter can be changed in the function), the first column needs to be a player ID, and the following are the players' day-by-day log information.
  
  Summarizing:

    Each row represents a player;
    The first column is the player's ID;
    The second is the log information for the first day of the data;
    The third is the log information for the second day and so forth.
  To represent the players' attendance, absence, or unknown status, the numbers -1, 0, and 1 are used as follows:
    
    -1 is used to represent a player that didn't log in but hasn't logged in the data;
    0 depicts an absence after a first attendance was accounted;
    1 means the player logged in.
  Input CSV file example:

    1, -1, -1, -1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1
    2, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0
    3, -1, -1, -1, -1, -1, -1, -1, -1, 1, 0, 0, 1, 1, 0

# Instructions:
  If you want to run all the paper's experiments:
  
    Download all files;
    Unzip the compressed files inside the same folder;
    The structure should be "\your_folder\Data", "\your_folder\Logs", "\your_folder\Results", "\your_folder\main.py" and "\your_folder\scripts.py";
    Run main.py;
    The results can be found in the Logs folder;
    If you want to check the results as charts, the results can be upload to the spreadsheets present in the "Results/Sheets" folder.
  If you want to check the results:
  
    Download the file Results.7z;
    Unzip it;
    In the CSV folder, there are all the CSV files outputted from the experiments deployment and used to generate the results spreadsheets;
    In the folder Sheets, there are the spreadsheets containing the results of the experiments formatted and charts to facilitate understanding.
  If you want to train a classifier with provided or new data to classify churn and utilize the proposed idea of redefinition:

    Download all files except for Results.7z;
    Unzip the compressed files inside the same folder;
    The structure should be "\your_folder\Data", "\your_folder\Logs", "\your_folder\main.py" and "\your_folder\scripts.py";
    For each new data (we advise daily runs), perform the following code;
    Import the data:
        data = load_csv('Data/YOUR_DATA_FILE.csv')
    Run the function <fv_calculation> or <ifv_calculation> to calculate, respectively, the FV or IFV:
        fv, la = scripts.fv_calculation(data)
        ifv, la = scripts.ifv_calculation(data)
    Label the players:
        players_labels_fv = scripts.label_players_fv(fv, la)
        players_labels_ifv = scripts.label_players_ifv(ifv, la)
    Check for historical labels (only exemplified for the FV but the same can be done for the IFV):
        if not file_exist('hist_labels_fv.p'):
            # Save the File
            pickle.dump(players_labels_fv, open('hist_labels_fv.p', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
            # Train the model using your features and the <players_labels_fv> labels
        else:
            # Load historical labels
            hist_labels_fv = scripts.load_pickle('hist_labels_fv.p')
            # Compare the past and current labels and calculate the F1-Score
            _, _, _, _, _, _, f1_score = scripts.calculate_f1_score(hist_labels_fv, players_labels_fv)
            # Calculate the CDCR
            cdcr = 1-f1_score
            # Verify if the CDCR is bigger than a user defined threshold (in this case 0.05)
            threshold = 0.05  # 5%
            if cdcr > threshold:
                # Save the File
                pickle.dump(players_labels_fv, open('hist_labels_fv.p', 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
                # Train the model using your features the new labels (i.e., players_labels_fv)
            else:
                # Train the model using your features the old labels (i.e., hist_labels_fv)

# main.py
  The main.py file contains the code to execute in the correct order all the steps to perform the paper's experiments. 
  It loads the data, calculates the FV and IFV metrics, and performs the experiments.
  It also contains an example of deployment in a production environment.
