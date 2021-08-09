from scripts import calculate_all_ifvs_fvs_las, load_csv, load_pickle, \
    run_aiide_ifv_experiment, run_aiide_redef_experiment


def main():
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


if __name__ == '__main__':
    main()
