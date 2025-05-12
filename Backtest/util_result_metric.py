def initiate_result_dict(para_dict):
    # result_dict initialization #
    result_dict = {'net_profit': [],
                   'mdd': [],
                   'mdd_pct': [],
                   'num_of_trade': [],
                   'win_rate': [],
                   'file_name': []}
    for keys in para_dict.keys():
        keys = keys.replace('_list', '')
        result_dict[keys] = []

    return result_dict


def record_result(result_dict, net_profit, mdd, mdd_pct, num_of_trade, win_rate, file_name, single_para_combination_dict):
    result_dict['net_profit'].append(net_profit)
    result_dict['mdd'].append(mdd)
    result_dict['mdd_pct'].append(mdd_pct)
    result_dict['num_of_trade'].append(num_of_trade)
    result_dict['win_rate'].append(win_rate)
    result_dict['file_name'].append(file_name)

    for keys in single_para_combination_dict.keys():
        result_dict[keys].append(single_para_combination_dict[keys])

    return result_dict