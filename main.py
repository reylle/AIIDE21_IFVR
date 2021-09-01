from pickle import dump, HIGHEST_PROTOCOL
from scripts import calculate_all_ifvs_fvs_las, calculate_f1_score, file_exist, fv_calculation, ifv_calculation, \
    label_players_fv, label_players_ifv, load_csv, load_pickle, run_aiide_ifv_experiment, run_aiide_redef_experiment


def main():
    # Perform all experiments
    # Import raw data
    data_lol = load_csv('Data/lol_player_log_history.csv')
    data_wow = load_csv('Data/wow_player_log_history.csv')

    # Calculate the metrics
    calculate_all_ifvs_fvs_las('LOL', data_lol)
    calculate_all_ifvs_fvs_las('WOW', data_wow)

    # Import pre-processed data
    data_lol_fvs = load_pickle('Data/LOL_all_fvs_las.p')
    data_lol_ifvs = load_pickle('Data/LOL_all_ifvs_las.p')
    data_wow_fvs = load_pickle('Data/WOW_all_fvs_las.p')
    data_wow_ifvs = load_pickle('Data/WOW_all_ifvs_las.p')

    # Define windows sizes
    windows_sizes = [7, 14, 21, 30, 60, 90, 180, 270]

    # Run the experiments scripts with and without redefinition for both LOL and WOW
    run_aiide_ifv_experiment('LOL', data_lol_fvs, data_lol_ifvs, windows_sizes)
    run_aiide_redef_experiment('LOL', data_lol_fvs, data_lol_ifvs, windows_sizes, 0.05)
    run_aiide_ifv_experiment('WOW', data_wow_fvs, data_wow_ifvs, windows_sizes)
    run_aiide_redef_experiment('WOW', data_wow_fvs, data_wow_ifvs, windows_sizes, 0.05)

    # # Production environment example
    # # Import the data
    # data = load_csv('Data/YOUR_DATA_FILE.csv')
    # # Run the function < fv_calculation > or < ifv_calculation > to calculate, respectively, the FV or IFV:
    # fv, la = fv_calculation(data)
    # ifv, la = ifv_calculation(data)
    # # Label the players
    # players_labels_fv = label_players_fv(fv, la)
    # players_labels_ifv = label_players_ifv(ifv, la)
    # # Check for historical labels(only exemplified for the FV but the same can be done for the IFV)
    # if not file_exist('hist_labels_fv.p'):
    #     # Save the File
    #     dump(players_labels_fv, open('hist_labels_fv.p', 'wb'), protocol=HIGHEST_PROTOCOL)
    #     # Train the model using your features and the <players_labels_fv> labels
    # else:
    #     # Load historical labels
    #     hist_labels_fv = load_pickle('hist_labels_fv.p')
    #     # Compare the past and current labels and calculate the F1-Score
    #     _, _, _, _, _, _, f1_score = calculate_f1_score(hist_labels_fv, players_labels_fv)
    #     # Calculate the CDCR
    #     cdcr = 1 - f1_score
    #     # Verify if the CDCR is bigger than a user defined threshold (in this case 0.05)
    #     threshold = 0.05  # 5%
    #     if cdcr > threshold:
    #         # Save the File
    #         dump(players_labels_fv, open('hist_labels_fv.p', 'wb'), protocol=HIGHEST_PROTOCOL)
    #         # Train the model using your features the new labels (i.e., players_labels_fv)
    #         print('Start you model training')
    #     else:
    #         # Train the model using your features the old labels (i.e., hist_labels_fv)
    #         print('Start you model training')


if __name__ == '__main__':
    main()
