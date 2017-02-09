from numpy import random as rn
import numpy as np
import pandas as pd


def transform_cite_dict(cite_dict):
    """

    :param cite_dict: dict {wA : [wBs]}
    :return: 2xN array, a[0] contains wA, a[1] contains wBs
    """

    lens = map(lambda x: len(x), cite_dict.values())
    d1 = sum(lens)
    arr = np.ndarray((2, d1), dtype=int)
    cs1 = np.cumsum(lens)
    cs0 = [0] + list(cs1[:-1])
    for k, val_list, x, y in zip(cite_dict.keys(), cite_dict.values(), cs0, cs1):
        arr[0, x:y] = [k]*(y-x)
        arr[1, x:y] = val_list
    return arr


def create_dummy_journals(df_cite, df_wj):
    """
    test only
    df_cite: df with 'wA' and 'wB' columns
    df_wj: df with 'w' and 'j' columns
    """

    wBs = df_cite['wB'].unique()
    ws = df_wj['w'].unique()
    outstanding_wBs = np.array(list(set(wBs) - set(ws)))
    print('unique journals:', len(df_wj['j'].unique()))
    js = df_wj['j'].unique()

    rns = rn.RandomState()
    n = 8
    j_inds = [rns.randint(n) for i in range(len(outstanding_wBs))]

    extra_js = js[j_inds]
    print(len(extra_js), len(outstanding_wBs))
    extra_df2 = pd.DataFrame({'w': outstanding_wBs, 'j': extra_js})
    df_wj_full = pd.concat([df_wj, extra_df2])
    print('unique journals at the end:', len(df_wj_full['j'].unique()))
    return df_wj_full


def create_dummy_cdatas(cdata, k=5, jm=8):
    """
    test only

    :param k: number of batches
    :param cdata:  [(w, j, w_refs_list)]
    :return: list of cdatas

    from cdata list : [(w, j, w_refs_list)]
    creates a list of k cdata-format dummy list (fake lists)
     [[(w_, j_, w_refs_list_)]]
    where w_ are taken from w_refs_list
    and j_ are taken from j at random
    """

    from numpy.random import RandomState
    wids_lists = map(lambda x: x[2], cdata)
    js_list = list(set(map(lambda x: x[1], cdata)))[:jm]
    wids_set = set([x for sublist in wids_lists for x in sublist])
    wids_list = list(wids_set)
    n = len(wids_set)
    delta = n / k
    inds = [(i * delta, (i + 1) * delta) for i in range(k)]

    dummy_wids_lists = [wids_list[ind[0]:ind[1]] for ind in inds]
    print(map(lambda x: len(x), dummy_wids_lists))

    rns = RandomState()
    rns.randint(len(js_list))
    dummy_js_lists = [[js_list[rns.randint(len(js_list))] for i in range(ind[1] - ind[0])] for ind in inds]
    emptys = [[[] for i in range(ind[1] - ind[0])] for ind in inds]

    print(map(lambda x: len(x), dummy_js_lists))

    cdata_list = [zip(x[0], x[1], x[2]) for x in zip(dummy_wids_lists, dummy_js_lists, emptys)]
    return cdata_list


def create_adj_df(df_cite, df_wj):
    """
    df_cite: df with 'wA' and 'wB' columns
    df_wj: df with 'w' and 'j' columns
    """

    print('unique journals in adj:', len(df_wj['j'].unique()))
    ws_unique = df_wj['w'].unique()
    df_cite_cut = df_cite.loc[df_cite['wB'].isin(ws_unique)]
    # log if the shapes of df_cite and df_cite_cut are different
    print(df_cite.shape[0], df_cite_cut.shape[0])
    df_agg = pd.merge(df_wj.rename(columns={'w': 'wA'}), df_cite_cut, how='right', on='wA')
    df_agg.rename(columns={'j': 'jA'}, inplace=True)
    print(df_agg.shape)
    df_agg = pd.merge(df_agg, df_wj.rename(columns={'w': 'wB'}), how='left', on='wB')
    df_agg.rename(columns={'j': 'jB'}, inplace=True)
    print(df_agg.shape)
    return df_agg


def extend_jj_df(sorted_js, df_agg):
    """
    extend jA to jB matrix
    (some journals may be not cited
    or cited and haven't published)
    the latter should not be possible

    :param sorted_js:
    :param df_agg:
    :return:
    """

    df_tot = pd.DataFrame(np.nan, columns=sorted_js, index=sorted_js)
    df_agg2 = df_agg[['jA', 'jB']].groupby(['jA', 'jB']).apply(lambda x: x.shape[0])
    df_adj = df_agg2.reset_index().pivot('jA', 'jB', 0)
    print(df_adj.shape)
    # no need to reindex df_adj, update() takes care of that
    df_tot.update(df_adj)
    df_tot = df_tot.fillna(0)
    return df_tot

