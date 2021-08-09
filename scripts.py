from csv import reader
from math import sqrt
from pickle import dump, HIGHEST_PROTOCOL, load


def average_absence_with_return(frequency: list):
    """
    Calculate a player's average Absence With Return and Last Absence
    :param frequency: A list containing a player's frequency
    :return: The player's average Absence With Return and Last Absence
    """
    absence = 0
    average = 0
    count = 0

    index = frequency.count('-1')
    # Disregard the days before a day played
    while index < len(frequency):
        # Sum all the absences
        while '0' in frequency[index]:
            absence += 1
            index += 1
            # If this is the last day
            if index >= len(frequency):
                if count == 0:
                    # None Absence With Return
                    return 0, absence
                else:
                    # Absences With Return averaged
                    return (average / count), absence
        # Sum an Absence With Return to the average
        if absence > 0:
            average += absence
            absence = 0
            count += 1
        index += 1

    if count == 0:
        # None Absence With Return and Last Absence
        return 0, 0
    else:
        # Absences With Return averaged and none Last Absence
        return (average / count), 0


def calculate_all_ifvs_fvs_las(dataset: str, data: dict) -> None:
    """
    Calculate all the Fixed Values, Individual Fixed Values and Last Absences from the players in the data

    :param dataset: The name of the game where the data was collected. Used for file naming only
    :param data: The players' frequency, key is the players' ID and values is a list starting from -1 until the first
    day of play. Later, each day played and not played should be represented by, respectively, 1 and 0.
    """
    all_ifvs_las = {}
    all_fvs_las = {}

    # Number of days in the dataset
    end = len(data[list(data.keys())[0]])
    # Calculate the metrics for various windows sizes
    # Starting from 1 day at the first dataset day, then 2 days encompassing day 1 and 2, and so on
    for x in range(1, end+1):
        # Get the data that occurs in the window
        cur_data_train, _ = split_data(data=data, offset_train=0, train_size=x,
                                       off_set_test=0, test_size=0)

        # Calculate the IFV and Last Absence for the players in the period
        cur_ifv, cur_ifv_la = ifv_calculation(cur_data_train)

        # Store the current day IFV
        all_ifvs_las[x] = {'ifv': cur_ifv, 'la': cur_ifv_la}

        # Calculate the FV and Last Absence for the players in the period
        cur_fv, cur_fv_la = fv_calculation(cur_data_train)

        # Store the current day FV
        all_fvs_las[x] = {'fv': cur_fv, 'la': cur_fv_la}

    # Dump the variables using pickle
    dump(all_ifvs_las, open('Data/{}_all_ifvs_las.p'.format(dataset), 'wb'), protocol=HIGHEST_PROTOCOL)
    dump(all_fvs_las, open('Data/{}_all_fvs_las.p'.format(dataset), 'wb'), protocol=HIGHEST_PROTOCOL)


def calculate_f1_score(test_labels: dict, true_labels: dict):
    """
    Calculate the F1-Score between the test and tru labels

    :param test_labels:
    :param true_labels:
    :return:
    """
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for key in test_labels.keys():
        if test_labels[key] == true_labels[key]:
            if true_labels[key] == 'Churner':
                tp += 1
            else:
                tn += 1
        else:
            if true_labels[key] == 'Churner':
                fn += 1
            else:
                fp += 1

    if tp == 0 and fp == 0:
        precision = 0
    else:
        precision = tp / (tp + fp)

    if tp == 0 and fn == 0:
        recall = 0
    else:
        recall = tp / (tp + fn)

    if precision == 0 and recall == 0:
        f1_score = 0
    else:
        f1_score = 2 * (precision * recall) / (precision + recall)

    return tp, fp, tn, fn, precision, recall, f1_score


def calculate_std_dev(average_general: float, average_individual: dict) -> float:
    """
    Calculate the standard deviation

    :param average_general: The average
    :param average_individual: A list containing all the averages that generate the average_general
    :return: The standard deviation
    """
    n = len(average_individual)
    summ = 0
    for key in average_individual:
        summ += pow((average_individual[key] - average_general), 2)
    summ /= n - 1

    return sqrt(summ)


def format_for_google_sheets(values: list) -> list:
    """
    Replace all '.' for ',' to be adequated to google sheets

    :param values: The values to be formated
    :return: The values formated
    """
    result = []
    for value in values:
        result += [str(value).replace('.', ',')]

    return result


def fv_calculation(data: dict):
    """
    Calculate the Fixed Value and Last Absence from the players' frequencies data

    :param data: The data containing the players' frequency
    :return: The players' Fixed Value and Last Absence
    """
    average = 0
    count = 0
    players_last_absence = {}
    for player in data.keys():
        absence = 0
        frequency = data[player]
        index = frequency.count('-1')
        # Disregard the days before a day played
        while index < len(frequency):
            # Sum all the absences
            while '0' in frequency[index]:
                absence += 1
                index += 1
                # If this is the last day
                if index >= len(frequency):
                    players_last_absence[player] = absence
                    break
            # Sum an Absence With Return to the average
            if absence > 0 and index < len(frequency):
                average += absence
                absence = 0
                count += 1
            index += 1
        if player not in players_last_absence:
            players_last_absence[player] = 0

    if count == 0:
        # None player had an Absence With Return but there are Last Absences
        return 0, players_last_absence
    else:
        # The players' Absence With Return averaged and the Last Absence
        return (average/count), players_last_absence


def ifv_calculation(data: dict):
    """
    Calculate the Individual Fixed Value and Last Absence from the players' frequencies data

    :param data: The data containing the players' frequency
    :return: The players' Individual Fixed Value and Last Absence
    """
    players_ifv = {}
    players_last_absence = {}
    for player in data.keys():
        history = data[player]
        absence, last_absence = average_absence_with_return(history)
        players_ifv[player] = absence
        players_last_absence[player] = last_absence

    return players_ifv, players_last_absence


def load_csv(file_full_path: str, delimiter=',') -> dict:
    """
    Load a CSV file containing players' frequencies with no header and return the data as a dict

    :param file_full_path: The CSV file full path with extension
    :param delimiter: The column delimiter
    :return: A dict containing the file content
    """
    # Verify if it is a CSV file
    if file_full_path.split('.')[-1] != 'csv':
        return dict()

    # Read and store the data
    data = {}
    with open(file_full_path, newline='') as csvfile:
        csv_reader = reader(csvfile, delimiter=delimiter)
        for row in csv_reader:
            if row[0] in data.keys():
                raise Exception(f"Player's ID duplicate: {row[0]}")
            else:
                data[row[0]] = row[1:]

    return data


def load_pickle(file_full_path: str):
    """
    Load a CSV file containing players' frequencies with no header and return the data as a dict

    :param file_full_path: The CSV file full path with extension
    """
    with open(file_full_path, 'rb') as fp:
        data = load(fp)
        fp.close()

    return data


def run_aiide_ifv_experiment(dataset: str, data_fvs: dict, data_ifvs: dict, windows_sizes: list):
    """
    Perform the paper experiment regards the comparison between the FV and IFV.
    Generate a file containing the averages of FV, Standard Deviation, TP, FP, TN, FN,
    Precision, Recall, F1-Score and CDCR

    :param dataset: The name of the game where the data was collected. Used for file naming only
    :param data_fvs: The players' Fixed Values
    :param data_ifvs: The players' Individual Fixed Values
    :param windows_sizes: A list containing the windows sizes to be used in the experiment
    """
    # Create Average log header
    with open('Logs/log_{}_{}.csv'.format(dataset, 'Average'), 'w') as file:
        file.write('Approach;Window Size;FV Average;Standard Deviation Average;TP Average;FP Average;TN Average;'
                   'FN Average;Precision Average;Recall Average;F1-Score Average;CDCR Average\n')

    fv_averages = []
    ifv_averages = []

    for window_size in windows_sizes:
        # Initialize variables
        # End index
        end = len(data_fvs)
        # Previous players' IFV
        players_prev_fv = None
        # Previous players' IFV
        players_prev_ifv = {}
        # Start index
        start = 0

        # Create FV log header
        with open('Logs/log_{}_{}_{}.csv'.format(dataset, 'FV', window_size), 'w') as file:
            file.write('FV;Standard Deviation;Number of Players;TP;FP;TN;FN;Precision;Recall;F1-Score;CDCR\n')

        # Create IFV log header
        with open('Logs/log_{}_{}_{}.csv'.format(dataset, 'IFV', window_size), 'w') as file:
            file.write('Number of Players;TP;FP;TN;FN;Precision;Recall;F1-Score;CDCR\n')

        players_prev_fv_average = []
        std_dev_average = []
        fv_tp_average = []
        fv_fp_average = []
        fv_tn_average = []
        fv_fn_average = []
        fv_precision_average = []
        fv_recall_average = []
        fv_f1_score_average = []
        fv_cdcr_average = []
        ifv_tp_average = []
        ifv_fp_average = []
        ifv_tn_average = []
        ifv_fn_average = []
        ifv_precision_average = []
        ifv_recall_average = []
        ifv_f1_score_average = []
        ifv_cdcr_average = []

        # Loop through the data set, starting from "start" jumping one day at a time and a window size of "window"
        while start + window_size <= end:
            # Reset variables
            labels_fv_prev = {}
            labels_ifv_curr = {}
            labels_ifv_prev = {}

            if players_prev_fv is None:
                # Gather the FV for the players in the period
                players_prev_fv = data_fvs[start + window_size]['fv']

            # Gather the IFV and last absence for the players in the period
            cur_ifv = data_ifvs[start + window_size]['ifv']
            cur_la = data_ifvs[start + window_size]['la']

            # If this is not the first IFV calculation, compare with the previous churn definition
            if len(players_prev_ifv) > 0:
                # Calculate the CDCR
                for player in players_prev_ifv.keys():
                    # Set the current IFV labels for the player
                    if cur_la[player] > cur_ifv[player]:
                        labels_ifv_curr[player] = 'Churner'
                    else:
                        labels_ifv_curr[player] = 'Non-Churner'

                    # Set the previous FV labels for the player
                    if cur_la[player] > players_prev_fv:
                        labels_fv_prev[player] = 'Churner'
                    else:
                        labels_fv_prev[player] = 'Non-Churner'

                    # Set the previous IFV labels for the player
                    if cur_la[player] > players_prev_ifv[player]:
                        labels_ifv_prev[player] = 'Churner'
                    else:
                        labels_ifv_prev[player] = 'Non-Churner'

                # Get the total number of players
                players_qnt = len(players_prev_ifv)
                # Calculate the Standard Deviation
                std_dev = calculate_std_dev(players_prev_fv, cur_ifv)
                # Calculate the FV TP, FP, TN, FN, Precision, Recall, and F1-Score
                tp, fp, tn, fn, precision, recall, f1_score = calculate_f1_score(labels_fv_prev, labels_ifv_curr)
                # Calculate the FV CDCR
                cdcr = 1 - f1_score
                # Fix format for Google Sheets
                fv_values = [players_prev_fv, std_dev, players_qnt, tp, fp, tn, fn, precision, recall, f1_score, cdcr]
                fv_formated = format_for_google_sheets(fv_values)

                # Store to calculate de averages
                players_prev_fv_average += [players_prev_fv]
                std_dev_average += [std_dev]
                fv_tp_average += [tp]
                fv_fp_average += [fp]
                fv_tn_average += [tn]
                fv_fn_average += [fn]
                fv_precision_average += [precision]
                fv_recall_average += [recall]
                fv_f1_score_average += [f1_score]
                fv_cdcr_average += [cdcr]

                # Calculate the IFV TP, FP, TN, FN, Precision, Recall, and F1-Score
                tp, fp, tn, fn, precision, recall, f1_score = calculate_f1_score(labels_ifv_prev, labels_ifv_curr)
                # Calculate the IFV CDCR
                cdcr = 1 - f1_score
                # Fix format for Google Sheets
                ifv_values = [players_qnt, tp, fp, tn, fn, precision, recall, f1_score, cdcr]
                ifv_formated = format_for_google_sheets(ifv_values)

                # Store to calculate de averages
                ifv_tp_average += [tp]
                ifv_fp_average += [fp]
                ifv_tn_average += [tn]
                ifv_fn_average += [fn]
                ifv_precision_average += [precision]
                ifv_recall_average += [recall]
                ifv_f1_score_average += [f1_score]
                ifv_cdcr_average += [cdcr]

                # Store FV log
                with open('Logs/log_{}_{}_{}.csv'.format(dataset, 'FV', window_size), 'a') as file:
                    file.write('{};{};{};{};{};{};{};{};{};{};{}\n'.format(fv_formated[0], fv_formated[1],
                                                                           fv_formated[2], fv_formated[3],
                                                                           fv_formated[4], fv_formated[5],
                                                                           fv_formated[6], fv_formated[7],
                                                                           fv_formated[8], fv_formated[9],
                                                                           fv_formated[10]))

                # Store IFV log
                with open('Logs/log_{}_{}_{}.csv'.format(dataset, 'IFV', window_size), 'a') as file:
                    file.write('{};{};{};{};{};{};{};{};{}\n'.format(ifv_formated[0], ifv_formated[1], ifv_formated[2],
                                                                     ifv_formated[3], ifv_formated[4], ifv_formated[5],
                                                                     ifv_formated[6], ifv_formated[7], ifv_formated[8]))
            else:
                # Store the current IFV to be used in the next loop
                players_prev_ifv = cur_ifv

            # Advances one day
            start += 1

        fv_averages += [[str(sum(players_prev_fv_average)/len(players_prev_fv_average)).replace('.', ','),
                         str(sum(std_dev_average)/len(std_dev_average)).replace('.', ','),
                         str(sum(fv_tp_average)/len(fv_tp_average)).replace('.', ','),
                         str(sum(fv_fp_average)/len(fv_fp_average)).replace('.', ','),
                         str(sum(fv_tn_average)/len(fv_tn_average)).replace('.', ','),
                         str(sum(fv_fn_average)/len(fv_fn_average)).replace('.', ','),
                         str(sum(fv_precision_average)/len(fv_precision_average)).replace('.', ','),
                         str(sum(fv_recall_average)/len(fv_recall_average)).replace('.', ','),
                         str(sum(fv_f1_score_average)/len(fv_f1_score_average)).replace('.', ','),
                         str(sum(fv_cdcr_average)/len(fv_cdcr_average)).replace('.', ',')]]

        ifv_averages += [['None',
                          'None',
                         str(sum(ifv_tp_average)/len(ifv_tp_average)).replace('.', ','),
                         str(sum(ifv_fp_average)/len(ifv_fp_average)).replace('.', ','),
                         str(sum(ifv_tn_average)/len(ifv_tn_average)).replace('.', ','),
                         str(sum(ifv_fn_average)/len(ifv_fn_average)).replace('.', ','),
                         str(sum(ifv_precision_average)/len(ifv_precision_average)).replace('.', ','),
                         str(sum(ifv_recall_average)/len(ifv_recall_average)).replace('.', ','),
                         str(sum(ifv_f1_score_average)/len(ifv_f1_score_average)).replace('.', ','),
                         str(sum(ifv_cdcr_average)/len(ifv_cdcr_average)).replace('.', ',')]]

    for x in range(0, len(fv_averages)):
        # Store the FV Average Log
        with open('Logs/log_{}_{}.csv'.format(dataset, 'Average'), 'a') as file:
            file.write('{};{};{};{};{};{};{};{};{};{};{};{}\n'.format('FV', windows_sizes[x], fv_averages[x][0],
                                                                      fv_averages[x][1], fv_averages[x][2],
                                                                      fv_averages[x][3], fv_averages[x][4],
                                                                      fv_averages[x][5], fv_averages[x][6],
                                                                      fv_averages[x][7], fv_averages[x][8],
                                                                      fv_averages[x][9]))

    for x in range(0, len(ifv_averages)):
        # Store the IFV Average Log
        with open('Logs/log_{}_{}.csv'.format(dataset, 'Average'), 'a') as file:
            file.write('{};{};{};{};{};{};{};{};{};{};{};{}\n'.format('IFV', windows_sizes[x], ifv_averages[x][0],
                                                                      ifv_averages[x][1], ifv_averages[x][2],
                                                                      ifv_averages[x][3], ifv_averages[x][4],
                                                                      ifv_averages[x][5], ifv_averages[x][6],
                                                                      ifv_averages[x][7], ifv_averages[x][8],
                                                                      ifv_averages[x][9]))


def run_aiide_redef_experiment(dataset: str, data_fvs: dict, data_ifvs: dict, windows_sizes: list, threshold: float):
    """
    Perform the paper experiment regards the comparison using and not using the redefinition.
    Generate a file containing the averages of FV, Standard Deviation, TP, FP, TN, FN,
    Precision, Recall, F1-Score and CDCR

    :param dataset: The name of the game where the data was collected. Used for file naming only
    :param data_fvs: The players' Fixed Values
    :param data_ifvs: The players' Individual Fixed Values
    :param windows_sizes: A list containing the windows sizes to be used in the experiment
    :param threshold: The threshold used in the CDCR comparison
    """
    # Create Average log header
    with open('Logs/log_{}_{}_Redef.csv'.format(dataset, 'Average'), 'w') as file:
        file.write(
            'Approach;Window Size;FV Average;Standard Deviation Average;TP Average;FP Average;TN Average;FN Average;'
            'Precision Average;Recall Average;F1-Score Average;CDCR Average\n')

    fv_averages = []
    ifv_averages = []

    for window_size in windows_sizes:
        # Initialize variables
        # End index
        end = len(data_fvs)
        # Previous players' IFV
        players_prev_fv = None
        # Previous players' IFV
        players_prev_ifv = {}
        # Start index
        start = 0

        # Create FV log header
        with open('Logs/log_{}_{}_{}_Redef.csv'.format(dataset, 'FV', window_size), 'w') as file:
            file.write('FV;Standard Deviation;Number of Players;TP;FP;TN;FN;Precision;Recall;F1-Score;CDCR\n')

        # Create IFV log header
        with open('Logs/log_{}_{}_{}_Redef.csv'.format(dataset, 'IFV', window_size), 'w') as file:
            file.write('Number of Players;TP;FP;TN;FN;Precision;Recall;F1-Score;CDCR\n')

        players_prev_fv_average = []
        std_dev_average = []
        fv_tp_average = []
        fv_fp_average = []
        fv_tn_average = []
        fv_fn_average = []
        fv_precision_average = []
        fv_recall_average = []
        fv_f1_score_average = []
        fv_cdcr_average = []
        ifv_tp_average = []
        ifv_fp_average = []
        ifv_tn_average = []
        ifv_fn_average = []
        ifv_precision_average = []
        ifv_recall_average = []
        ifv_f1_score_average = []
        ifv_cdcr_average = []

        # Loop through the data set, starting from "start" jumping one day at a time and a window size of "window"
        while start + window_size <= end:
            # Reset variables
            labels_fv_prev = {}
            labels_ifv_curr = {}
            labels_ifv_prev = {}

            if players_prev_fv is None:
                # Gather the FV for the players in the period
                players_prev_fv = data_fvs[start + window_size]['fv']

            # Gather the IFV and last absence for the players in the period
            cur_ifv = data_ifvs[start + window_size]['ifv']
            cur_la = data_ifvs[start + window_size]['la']

            # If this is not the first IFV calculation, compare with the previous churn definition
            if len(players_prev_ifv) > 0:
                # Calculate the CDCR
                for player in players_prev_ifv.keys():
                    # Set the current IFV labels for the player
                    if cur_la[player] > cur_ifv[player]:
                        labels_ifv_curr[player] = 'Churner'
                    else:
                        labels_ifv_curr[player] = 'Non-Churner'

                    # Set the previous FV labels for the player
                    if cur_la[player] > players_prev_fv:
                        labels_fv_prev[player] = 'Churner'
                    else:
                        labels_fv_prev[player] = 'Non-Churner'

                    # Set the previous IFV labels for the player
                    if cur_la[player] > players_prev_ifv[player]:
                        labels_ifv_prev[player] = 'Churner'
                    else:
                        labels_ifv_prev[player] = 'Non-Churner'

                # Get the total number of players
                players_qnt = len(players_prev_ifv)
                # Calculate the Standard Deviation
                std_dev = calculate_std_dev(players_prev_fv, cur_ifv)
                # Calculate the FV TP, FP, TN, FN, Precision, Recall, and F1-Score
                tp, fp, tn, fn, precision, recall, f1_score = calculate_f1_score(labels_fv_prev,
                                                                                 labels_ifv_curr)
                # Calculate the FV CDCR
                fv_cdcr = 1 - f1_score
                # Fix format for Google Sheets
                fv_values = [players_prev_fv, std_dev, players_qnt, tp, fp, tn, fn, precision, recall, f1_score,
                             fv_cdcr]
                fv_formated = format_for_google_sheets(fv_values)

                # Store to calculate de averages
                players_prev_fv_average += [players_prev_fv]
                std_dev_average += [std_dev]
                fv_tp_average += [tp]
                fv_fp_average += [fp]
                fv_tn_average += [tn]
                fv_fn_average += [fn]
                fv_precision_average += [precision]
                fv_recall_average += [recall]
                fv_f1_score_average += [f1_score]
                fv_cdcr_average += [fv_cdcr]

                # Calculate the IFV TP, FP, TN, FN, Precision, Recall, and F1-Score
                tp, fp, tn, fn, precision, recall, f1_score = calculate_f1_score(labels_ifv_prev,
                                                                                 labels_ifv_curr)
                # Calculate the IFV CDCR
                ifv_cdcr = 1 - f1_score
                # Fix format for Google Sheets
                ifv_values = [players_qnt, tp, fp, tn, fn, precision, recall, f1_score, ifv_cdcr]
                ifv_formated = format_for_google_sheets(ifv_values)

                # Store to calculate de averages
                ifv_tp_average += [tp]
                ifv_fp_average += [fp]
                ifv_tn_average += [tn]
                ifv_fn_average += [fn]
                ifv_precision_average += [precision]
                ifv_recall_average += [recall]
                ifv_f1_score_average += [f1_score]
                ifv_cdcr_average += [ifv_cdcr]

                # Store FV log
                with open('Logs/log_{}_{}_{}_Redef.csv'.format(dataset, 'FV', window_size), 'a') as file:
                    file.write('{};{};{};{};{};{};{};{};{};{};{}\n'.format(fv_formated[0], fv_formated[1],
                                                                           fv_formated[2], fv_formated[3],
                                                                           fv_formated[4], fv_formated[5],
                                                                           fv_formated[6], fv_formated[7],
                                                                           fv_formated[8], fv_formated[9],
                                                                           fv_formated[10]))

                # Store IFV log
                with open('Logs/log_{}_{}_{}_Redef.csv'.format(dataset, 'IFV', window_size), 'a') as file:
                    file.write(
                        '{};{};{};{};{};{};{};{};{}\n'.format(ifv_formated[0], ifv_formated[1], ifv_formated[2],
                                                              ifv_formated[3], ifv_formated[4], ifv_formated[5],
                                                              ifv_formated[6], ifv_formated[7],
                                                              ifv_formated[8]))

                # Verify the need to =redefine the FV
                if fv_cdcr >= threshold:
                    # Re-define the FV
                    players_prev_fv = data_fvs[start + window_size]['fv']
                # Verify the need to re-define the IFV
                if ifv_cdcr >= threshold:
                    # Re-define the IFV
                    players_prev_ifv = cur_ifv

            else:
                # Store the current IFV to be used in the next loop
                players_prev_ifv = cur_ifv

            # Advances one day
            start += 1

        fv_averages += [[str(sum(players_prev_fv_average) / len(players_prev_fv_average)).replace('.', ','),
                         str(sum(std_dev_average) / len(std_dev_average)).replace('.', ','),
                         str(sum(fv_tp_average) / len(fv_tp_average)).replace('.', ','),
                         str(sum(fv_fp_average) / len(fv_fp_average)).replace('.', ','),
                         str(sum(fv_tn_average) / len(fv_tn_average)).replace('.', ','),
                         str(sum(fv_fn_average) / len(fv_fn_average)).replace('.', ','),
                         str(sum(fv_precision_average) / len(fv_precision_average)).replace('.', ','),
                         str(sum(fv_recall_average) / len(fv_recall_average)).replace('.', ','),
                         str(sum(fv_f1_score_average) / len(fv_f1_score_average)).replace('.', ','),
                         str(sum(fv_cdcr_average) / len(fv_cdcr_average)).replace('.', ',')]]

        ifv_averages += [['None',
                          'None',
                          str(sum(ifv_tp_average) / len(ifv_tp_average)).replace('.', ','),
                          str(sum(ifv_fp_average) / len(ifv_fp_average)).replace('.', ','),
                          str(sum(ifv_tn_average) / len(ifv_tn_average)).replace('.', ','),
                          str(sum(ifv_fn_average) / len(ifv_fn_average)).replace('.', ','),
                          str(sum(ifv_precision_average) / len(ifv_precision_average)).replace('.', ','),
                          str(sum(ifv_recall_average) / len(ifv_recall_average)).replace('.', ','),
                          str(sum(ifv_f1_score_average) / len(ifv_f1_score_average)).replace('.', ','),
                          str(sum(ifv_cdcr_average) / len(ifv_cdcr_average)).replace('.', ',')]]

    for x in range(0, len(fv_averages)):
        # Store the FV Average Log
        with open('Logs/log_{}_{}_Redef.csv'.format(dataset, 'Average'), 'a') as file:
            file.write('{};{};{};{};{};{};{};{};{};{};{};{}\n'.format('FV', windows_sizes[x], fv_averages[x][0],
                                                                      fv_averages[x][1], fv_averages[x][2],
                                                                      fv_averages[x][3], fv_averages[x][4],
                                                                      fv_averages[x][5], fv_averages[x][6],
                                                                      fv_averages[x][7], fv_averages[x][8],
                                                                      fv_averages[x][9]))

    for x in range(0, len(ifv_averages)):
        # Store the IFV Average Log
        with open('Logs/log_{}_{}_Redef.csv'.format(dataset, 'Average'), 'a') as file:
            file.write(
                '{};{};{};{};{};{};{};{};{};{};{};{}\n'.format('IFV', windows_sizes[x], ifv_averages[x][0],
                                                               ifv_averages[x][1], ifv_averages[x][2],
                                                               ifv_averages[x][3], ifv_averages[x][4],
                                                               ifv_averages[x][5], ifv_averages[x][6],
                                                               ifv_averages[x][7], ifv_averages[x][8],
                                                               ifv_averages[x][9]))


def split_data(data: dict, offset_train: int, train_size: int, off_set_test: int, test_size: int):
    """
    Separate the lists inside a dict into train and test

    :param data: The data used in the split
    :param offset_train: The training data offset
    :param train_size: The training data size
    :param off_set_test: The test data offset
    :param test_size: The test data size
    :return: The dict with the list inside of it shortener
    """
    train_window = {}
    test_window = {}
    for key in data.keys():
        train_window[key] = data[key][offset_train:offset_train + train_size]
        test_window[key] = data[key][offset_train + train_size + off_set_test:
                                     offset_train + train_size + off_set_test + test_size]

    return train_window, test_window
